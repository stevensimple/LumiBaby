import SwiftUI
import Combine

@MainActor
class SleepViewModel: ObservableObject {
    @Published var tonightSession: SleepSessionInfo?
    @Published var history: [DailySummary] = []
    @Published var weekly: WeeklyTrend?
    @Published var isLoading = false
    @Published var currentSensorId: String = ""

    func load(sensorId: String) async {
        guard !sensorId.isEmpty else { return }
        currentSensorId = sensorId
        isLoading = true
        async let tonight = APIService.shared.fetchTonightSleep(sensorId: sensorId)
        async let hist    = APIService.shared.fetchSleepHistory(sensorId: sensorId, days: 7)
        async let trend   = APIService.shared.fetchWeeklyTrend(sensorId: sensorId)
        tonightSession = try? await tonight
        history        = (try? await hist) ?? []
        weekly         = try? await trend
        isLoading      = false
    }

    var durationText: String {
        guard let mins = tonightSession?.durationMinutes, mins > 0 else { return "—" }
        let h = Int(mins / 60), m = Int(mins) % 60
        return h > 0 ? "\(h)h \(m)m" : "\(m) min"
    }

    var startTimeText: String {
        guard let t = tonightSession?.startTime else { return "—" }
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let date = f.date(from: t) else { return t }
        let df = DateFormatter(); df.timeStyle = .short
        return df.string(from: date)
    }

    var qualityColor: Color {
        guard let score = tonightSession?.sleepScore else { return LumiColor.textSecondary }
        if score >= 75 { return LumiColor.calm }
        if score >= 50 { return LumiColor.movement }
        return LumiColor.alert
    }

    var insightText: String {
        guard let session = tonightSession, session.active else { return "Aucune donnée cette nuit" }
        guard let score = session.sleepScore else { return "Collecte des données en cours…" }
        if score >= 80 { return "Nuit très calme — bébé dort bien" }
        if score >= 65 { return "Bonne nuit dans l'ensemble" }
        if score >= 50 { return "Nuit légèrement agitée" }
        return "Nuit agitée — plusieurs réveils"
    }
}
