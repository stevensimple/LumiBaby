import SwiftUI
import Combine

@MainActor
class HomeViewModel: ObservableObject {
    @Published var status: RoomStatus?
    @Published var isLoading = true

    private var cancellables = Set<AnyCancellable>()

    init() {
        WebSocketService.shared.$latestStatus
            .receive(on: DispatchQueue.main)
            .sink { [weak self] s in
                if let s { self?.status = s; self?.isLoading = false }
            }
            .store(in: &cancellables)
    }

    // MARK: - State

    var sleepState: String { status?.sleep?.state ?? "awake" }
    var isSleeping: Bool { sleepState == "sleeping" }
    var babyDetected: Bool { status?.baby.detected ?? false }

    // MARK: - Display text (French, no jargon)

    var mainStateText: String {
        guard let s = status else { return "Connexion…" }
        if !s.baby.detected { return "Bébé non détecté" }
        switch s.movement.level {
        case "calm":
            return isSleeping ? "Sommeil paisible" : "Au calme"
        case "light":
            return "Activité légère"
        case "agitated":
            return "Agité"
        case "very_agitated":
            return "Très agité"
        default:
            return "En observation"
        }
    }

    var mainStateColor: Color {
        guard let s = status else { return LumiColor.primary }
        if !s.baby.detected { return LumiColor.textSecondary }
        switch s.movement.level {
        case "calm":          return LumiColor.calm
        case "light":         return LumiColor.primary
        case "agitated":      return LumiColor.movement
        case "very_agitated": return LumiColor.alert
        default:              return LumiColor.primary
        }
    }

    var mainStateIcon: String {
        guard let s = status else { return "wifi.slash" }
        if !s.baby.detected { return "questionmark.circle" }
        if isSleeping { return "moon.zzz.fill" }
        switch s.movement.level {
        case "calm":          return "moon.zzz.fill"
        case "light":         return "figure.roll"
        case "agitated":      return "waveform.path"
        case "very_agitated": return "exclamationmark.triangle.fill"
        default:              return "moon.stars"
        }
    }

    var sleepDurationText: String {
        guard let mins = status?.sleep?.durationMinutes, mins > 0 else { return "—" }
        if mins < 60 { return "\(Int(mins)) min" }
        let h = Int(mins / 60)
        let m = Int(mins) % 60
        return m > 0 ? "\(h)h \(m)m" : "\(h)h"
    }

    var lastMovementText: String {
        guard let mins = status?.inactivityMinutes else { return "—" }
        if mins < 1 { return "À l'instant" }
        if mins < 60 { return "il y a \(Int(mins)) min" }
        return "il y a \(Int(mins / 60))h"
    }

    var activityScore: Int { status?.activityScore ?? 0 }

    var scoreLabel: String {
        let s = activityScore
        if !babyDetected { return "Non détecté" }
        if s >= 80 { return "Bonne nuit" }
        if s >= 60 { return "Au repos" }
        if s >= 40 { return "Actif" }
        return "Agité"
    }

    var inactivityWarning: String? {
        guard let s = status, s.baby.detected, s.inactivityMinutes >= 20 else { return nil }
        return "Aucun mouvement depuis \(Int(s.inactivityMinutes)) min"
    }
}
