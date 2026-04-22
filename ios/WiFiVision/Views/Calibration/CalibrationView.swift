import SwiftUI

struct CalibrationView: View {
    @StateObject private var vm = CalibrationViewModel()
    @State private var selectedSensorId = ""
    @State private var sensors: [Sensor] = []

    var body: some View {
        NavigationStack {
            Group {
                if vm.isComplete {
                    CalibrationCompleteView(score: vm.qualityScore ?? 0) { vm.reset() }
                } else if vm.isRunning || vm.currentPhaseIndex > 0 {
                    CalibrationActiveView(vm: vm)
                } else {
                    CalibrationStartView(sensors: sensors, selectedId: $selectedSensorId) {
                        guard !selectedSensorId.isEmpty else { return }
                        vm.start(sensorId: selectedSensorId)
                    }
                }
            }
            .navigationTitle("Setup")
            .task { sensors = (try? await APIService.shared.fetchSensors()) ?? [] }
        }
    }
}

private struct CalibrationStartView: View {
    let sensors: [Sensor]
    @Binding var selectedId: String
    let onStart: () -> Void

    var body: some View {
        VStack(spacing: 32) {
            Spacer()
            Image(systemName: "figure.child.and.lock").font(.system(size: 64)).foregroundStyle(.blue)
            VStack(spacing: 8) {
                Text("Set Up the Monitor").font(.title2.bold())
                Text("Takes about 2 minutes. Helps the sensor learn your baby's space.")
                    .font(.subheadline).foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
            if !sensors.isEmpty {
                Picker("Sensor", selection: $selectedId) {
                    Text("Select sensor").tag("")
                    ForEach(sensors) { s in Text(s.name).tag(s.sensorId) }
                }
                .pickerStyle(.menu)
                .padding()
                .background(Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .padding(.horizontal)
            }
            Button("Start Setup", action: onStart)
                .buttonStyle(.borderedProminent)
                .disabled(selectedId.isEmpty)
            Spacer()
        }
        .padding()
    }
}

private struct CalibrationActiveView: View {
    @ObservedObject var vm: CalibrationViewModel

    var body: some View {
        VStack(spacing: 32) {
            ProgressView(value: vm.progress + (1.0 / Double(CalibrationPhase.allCases.count)) * (1.0 - Double(vm.countdown) / 30.0))
                .padding(.horizontal)
            VStack(spacing: 4) {
                Text("Step \(vm.currentPhaseIndex + 1) of \(vm.phases.count)")
                    .font(.caption).foregroundStyle(.secondary)
                Text(vm.currentPhase.title).font(.title.bold())
            }
            Image(systemName: vm.currentPhase.symbolName)
                .font(.system(size: 80)).foregroundStyle(.blue)
            Text(vm.currentPhase.instruction)
                .font(.body).foregroundStyle(.secondary)
                .multilineTextAlignment(.center).padding(.horizontal)
            ZStack {
                Circle().stroke(Color(.systemGray5), lineWidth: 8)
                Circle().trim(from: 0, to: CGFloat(vm.countdown) / 30.0)
                    .stroke(.blue, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .animation(.linear(duration: 1), value: vm.countdown)
                Text("\(vm.countdown)")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
            }
            .frame(width: 120, height: 120)
            if let error = vm.error { Text(error).font(.caption).foregroundStyle(.red) }
            Spacer()
        }
        .padding()
    }
}

private struct CalibrationCompleteView: View {
    let score: Double
    let onReset: () -> Void
    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "checkmark.circle.fill").font(.system(size: 80)).foregroundStyle(.green)
            Text("Setup Complete").font(.title.bold())
            VStack(spacing: 8) {
                Text("Signal Quality").font(.caption).foregroundStyle(.secondary)
                Text("\(Int(score * 100))%").font(.largeTitle.bold())
                    .foregroundStyle(score >= 0.7 ? .green : score >= 0.4 ? .orange : .red)
            }
            Text(score >= 0.7
                 ? "The sensor is ready. Monitoring is active."
                 : score >= 0.4
                 ? "Good signal. Try moving the sensor closer to the crib for better results."
                 : "Weak signal. Reposition the sensor closer to the crib and try again.")
                .font(.subheadline).foregroundStyle(.secondary)
                .multilineTextAlignment(.center).padding(.horizontal)
            Button("Run Setup Again", action: onReset).buttonStyle(.bordered)
            Spacer()
        }
        .padding()
    }
}
