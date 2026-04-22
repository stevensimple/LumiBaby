import Foundation

struct RoomStatus: Codable {
    let timestamp: String
    let sensorId: String
    let baby: BabyPresence
    let movement: MovementStatus
    let signalPattern: SignalPatternStatus
    let activityScore: Int
    let inactivityMinutes: Double
    let sleep: SleepLiveInfo?

    enum CodingKeys: String, CodingKey {
        case timestamp, baby, movement, sleep
        case sensorId          = "sensor_id"
        case signalPattern     = "signal_pattern"
        case activityScore     = "activity_score"
        case inactivityMinutes = "inactivity_minutes"
    }
}

struct BabyPresence: Codable {
    let detected: Bool
    let confidence: Double
}

struct MovementStatus: Codable {
    let level: String
    let value: Double
    let confidence: Double
}

struct SignalPatternStatus: Codable {
    let rhythmic: Bool
    let confidence: Double
    let note: String
}

struct SleepLiveInfo: Codable {
    let state: String
    let sessionId: String?
    let startTime: String?
    let durationMinutes: Double?
    let wakeEventsCount: Int?
    let calmRatio: Double?

    enum CodingKeys: String, CodingKey {
        case state
        case sessionId       = "session_id"
        case startTime       = "start_time"
        case durationMinutes = "duration_minutes"
        case wakeEventsCount = "wake_events_count"
        case calmRatio       = "calm_ratio"
    }
}

struct WSMessage: Codable {
    let type: String
    let data: RoomStatus?
    let event: WSEvent?
    let alert: WSAlert?
}

struct WSEvent: Codable {
    let id: String
    let type: String
    let timestamp: String
    let sensorId: String
    enum CodingKeys: String, CodingKey {
        case id, type, timestamp
        case sensorId = "sensor_id"
    }
}

struct WSAlert: Codable {
    let id: String
    let type: String
    let message: String
    let severity: String
}
