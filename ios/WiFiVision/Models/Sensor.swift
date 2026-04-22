import Foundation

struct Sensor: Codable, Identifiable {
    let id: String
    let sensorId: String
    let name: String
    let location: String?
    let isOnline: Bool
    let lastSeen: String?

    enum CodingKeys: String, CodingKey {
        case name, location
        case sensorId = "sensor_id"
        case isOnline = "is_online"
        case lastSeen = "last_seen"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        sensorId = try c.decode(String.self, forKey: .sensorId)
        id = sensorId
        name = try c.decode(String.self, forKey: .name)
        location = try c.decodeIfPresent(String.self, forKey: .location)
        isOnline = try c.decode(Bool.self, forKey: .isOnline)
        lastSeen = try c.decodeIfPresent(String.self, forKey: .lastSeen)
    }
}

struct SensorHealth: Codable {
    let online: Bool
    let lastSeen: String?
    let signalQuality: Double
    let packetRate: Double

    enum CodingKeys: String, CodingKey {
        case online
        case lastSeen = "last_seen"
        case signalQuality = "signal_quality"
        case packetRate = "packet_rate"
    }
}
