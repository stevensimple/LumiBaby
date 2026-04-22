import Foundation

@MainActor
class HistoryViewModel: ObservableObject {
    @Published var presenceHistory: [[String: Any]] = []
    @Published var breathingHistory: [[String: Any]] = []
    @Published var isLoading = false

    func load(sensorId: String? = nil) async {
        isLoading = true
        async let presence = APIService.shared.fetchPresenceHistory(sensorId: sensorId)
        async let breathing = APIService.shared.fetchBreathingHistory(sensorId: sensorId)
        presenceHistory = (try? await presence) ?? []
        breathingHistory = (try? await breathing) ?? []
        isLoading = false
    }

    func formatTime(_ iso: String) -> String {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let date = f.date(from: iso) else { return iso }
        let df = DateFormatter()
        df.dateStyle = .short
        df.timeStyle = .short
        return df.string(from: date)
    }
}
