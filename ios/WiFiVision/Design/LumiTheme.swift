import SwiftUI

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 6:
            (a, r, g, b) = (255, (int >> 16) & 0xFF, (int >> 8) & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(.sRGB,
                  red: Double(r) / 255,
                  green: Double(g) / 255,
                  blue: Double(b) / 255,
                  opacity: Double(a) / 255)
    }
}

// MARK: - Lumi Design System

enum LumiColor {
    static let background    = Color(hex: "0A0E1A")
    static let card          = Color(hex: "131829")
    static let cardLight     = Color(hex: "1C2340")
    static let primary       = Color(hex: "4E9AF1")
    static let calm          = Color(hex: "34C759")
    static let movement      = Color(hex: "FF9F0A")
    static let alert         = Color(hex: "FF453A")
    static let textPrimary   = Color.white
    static let textSecondary = Color.white.opacity(0.55)
    static let separator     = Color.white.opacity(0.08)
}

enum LumiFont {
    static let largeTitle  = Font.system(size: 34, weight: .bold,     design: .rounded)
    static let title       = Font.system(size: 24, weight: .bold,     design: .rounded)
    static let title2      = Font.system(size: 20, weight: .semibold, design: .rounded)
    static let headline    = Font.system(size: 17, weight: .semibold)
    static let body        = Font.system(size: 15, weight: .regular)
    static let caption     = Font.system(size: 12, weight: .regular)
    static let captionBold = Font.system(size: 12, weight: .semibold)
}

// MARK: - Reusable Card modifier

struct LumiCard: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(LumiColor.card)
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

extension View {
    func lumiCard() -> some View {
        modifier(LumiCard())
    }
}
