import Foundation

enum CalibrationPhase: String, CaseIterable {
    case empty = "empty"
    case still = "still"
    case movement = "movement"
    case breathing = "breathing"

    var title: String {
        switch self {
        case .empty: return "Empty Room"
        case .still: return "Stand Still"
        case .movement: return "Walk Slowly"
        case .breathing: return "Sit & Breathe"
        }
    }

    var instruction: String {
        switch self {
        case .empty: return "Leave the room completely empty"
        case .still: return "Stand still in the center of the room"
        case .movement: return "Walk slowly around the room"
        case .breathing: return "Sit down and breathe normally"
        }
    }

    var symbolName: String {
        switch self {
        case .empty: return "house"
        case .still: return "figure.stand"
        case .movement: return "figure.walk"
        case .breathing: return "lungs"
        }
    }
}

struct CalibrationResult: Codable {
    let sessionId: String
    let status: String
    let signalQualityScore: Double?
    let baselineVariance: Double?

    enum CodingKeys: String, CodingKey {
        case status
        case sessionId = "session_id"
        case signalQualityScore = "signal_quality_score"
        case baselineVariance = "baseline_variance"
    }
}
