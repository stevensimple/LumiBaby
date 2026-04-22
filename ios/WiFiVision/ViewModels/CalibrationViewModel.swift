import SwiftUI

@MainActor
class CalibrationViewModel: ObservableObject {
    @Published var currentPhaseIndex = 0
    @Published var countdown = 30
    @Published var isRunning = false
    @Published var isComplete = false
    @Published var qualityScore: Double?
    @Published var error: String?

    private var sessionId: String?
    private var timer: Timer?
    private var sensorId: String = ""

    let phases = CalibrationPhase.allCases

    var currentPhase: CalibrationPhase { phases[currentPhaseIndex] }
    var progress: Double { Double(currentPhaseIndex) / Double(phases.count) }

    func start(sensorId: String) {
        self.sensorId = sensorId
        currentPhaseIndex = 0
        isComplete = false
        qualityScore = nil
        error = nil
        beginPhase()
    }

    private func beginPhase() {
        isRunning = true
        countdown = 30
        Task {
            do {
                sessionId = try await APIService.shared.startCalibration(sensorId: sensorId, phase: currentPhase.rawValue)
                startCountdown()
            } catch {
                self.error = error.localizedDescription
                isRunning = false
            }
        }
    }

    private func startCountdown() {
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            if self.countdown > 0 {
                self.countdown -= 1
            } else {
                self.timer?.invalidate()
                self.advancePhase()
            }
        }
    }

    private func advancePhase() {
        Task {
            guard let sid = sessionId else { return }
            do {
                let result = try await APIService.shared.completeCalibration(sessionId: sid)
                if currentPhaseIndex < phases.count - 1 {
                    currentPhaseIndex += 1
                    beginPhase()
                } else {
                    qualityScore = result.signalQualityScore
                    isRunning = false
                    isComplete = true
                }
            } catch {
                self.error = error.localizedDescription
                isRunning = false
            }
        }
    }

    func reset() {
        timer?.invalidate()
        currentPhaseIndex = 0
        countdown = 30
        isRunning = false
        isComplete = false
        qualityScore = nil
        error = nil
        sessionId = nil
    }
}
