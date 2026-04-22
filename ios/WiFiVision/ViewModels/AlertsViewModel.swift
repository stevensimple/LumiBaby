import SwiftUI

@MainActor
class AlertsViewModel: ObservableObject {
    @Published var alerts: [AlertItem] = []
    @Published var isLoading = false

    func load() async {
        isLoading = true
        alerts = (try? await APIService.shared.fetchAlerts(acknowledged: false)) ?? []
        isLoading = false
    }

    func acknowledge(id: String) async {
        try? await APIService.shared.acknowledgeAlert(id: id)
        alerts.removeAll { $0.id == id }
    }
}
