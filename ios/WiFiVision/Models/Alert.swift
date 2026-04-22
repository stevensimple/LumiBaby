import Foundation

struct AlertItem: Codable, Identifiable {
    let id: String
    let sensorId: String?
    let type: String
    let message: String
    let severity: String
    let createdAt: String
    let acknowledged: Bool

    enum CodingKeys: String, CodingKey {
        case id, type, message, severity, acknowledged
        case sensorId = "sensor_id"
        case createdAt = "created_at"
    }
}
