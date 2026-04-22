import SwiftUI

@MainActor
class SensorsViewModel: ObservableObject {
    @Published var sensors: [Sensor] = []
    @Published var isLoading = false
    @Published var error: String?

    func load() async {
        isLoading = true
        error = nil
        do {
            sensors = try await APIService.shared.fetchSensors()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }
}
