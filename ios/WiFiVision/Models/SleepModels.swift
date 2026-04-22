import Foundation

struct SleepSessionInfo: Codable {
    let active: Bool
    let sessionId: String?
    let state: String?
    let startTime: String?
    let endTime: String?
    let durationMinutes: Double?
    let calmRatio: Double?
    let wakeEventsCount: Int?
    let sleepScore: Int?
    let qualityLabel: String?
    let timeline: [TimelinePoint]?
    let message: String?

    enum CodingKeys: String, CodingKey {
        case active, state, message, timeline
        case sessionId      = "session_id"
        case startTime      = "start_time"
        case endTime        = "end_time"
        case durationMinutes = "duration_minutes"
        case calmRatio      = "calm_ratio"
        case wakeEventsCount = "wake_events_count"
        case sleepScore     = "sleep_score"
        case qualityLabel   = "quality_label"
    }
}

struct TimelinePoint: Codable, Identifiable {
    let t: Double
    let level: String
    var id: Double { t }
}

struct DailySummary: Codable, Identifiable {
    let id: String
    let date: String
    let totalSleepMinutes: Double
    let wakeCount: Int
    let longestStreakMinutes: Double
    let sleepScore: Int
    let qualityLabel: String
    let sessionCount: Int
    let avgSleepStartHour: Double?

    enum CodingKeys: String, CodingKey {
        case id, date
        case totalSleepMinutes    = "total_sleep_minutes"
        case wakeCount            = "wake_count"
        case longestStreakMinutes  = "longest_streak_minutes"
        case sleepScore           = "sleep_score"
        case qualityLabel         = "quality_label"
        case sessionCount         = "session_count"
        case avgSleepStartHour    = "avg_sleep_start_hour"
    }
}

struct WeeklyTrend: Codable {
    let days: [DaySummary]
    let avgScore: Int
    let consistencyScore: Int
    let avgDurationHours: Double

    enum CodingKeys: String, CodingKey {
        case days
        case avgScore         = "avg_score"
        case consistencyScore = "consistency_score"
        case avgDurationHours = "avg_duration_hours"
    }
}

struct DaySummary: Codable, Identifiable {
    let date: String
    let sleepScore: Int
    let qualityLabel: String
    let totalHours: Double
    let wakeCount: Int
    var id: String { date }

    enum CodingKeys: String, CodingKey {
        case date
        case sleepScore   = "sleep_score"
        case qualityLabel = "quality_label"
        case totalHours   = "total_hours"
        case wakeCount    = "wake_count"
    }
}
