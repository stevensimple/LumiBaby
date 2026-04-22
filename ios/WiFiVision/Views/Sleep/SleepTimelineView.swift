import SwiftUI

struct SleepTimelineView: View {
    let points: [TimelinePoint]
    let startTime: Date?

    private func color(for level: String) -> Color {
        switch level {
        case "calm":          return LumiColor.calm
        case "light":         return LumiColor.primary
        case "agitated":      return LumiColor.movement
        case "very_agitated": return LumiColor.alert
        default:              return LumiColor.card
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Activité nocturne")
                .font(LumiFont.captionBold)
                .foregroundStyle(LumiColor.textSecondary)

            if points.isEmpty {
                RoundedRectangle(cornerRadius: 6)
                    .fill(LumiColor.card)
                    .frame(height: 36)
                    .overlay(
                        Text("Données insuffisantes")
                            .font(LumiFont.caption)
                            .foregroundStyle(LumiColor.textSecondary)
                    )
            } else {
                GeometryReader { geo in
                    let totalDuration = (points.last?.t ?? 1) - (points.first?.t ?? 0)
                    HStack(spacing: 1) {
                        ForEach(Array(points.enumerated()), id: \.offset) { i, point in
                            let nextT = i + 1 < points.count ? points[i + 1].t : point.t + 300
                            let segDuration = nextT - point.t
                            let fraction = totalDuration > 0
                                ? CGFloat(segDuration / totalDuration)
                                : 1 / CGFloat(points.count)
                            RoundedRectangle(cornerRadius: 3)
                                .fill(color(for: point.level))
                                .frame(width: geo.size.width * fraction)
                        }
                    }
                    .frame(height: 36)
                }
                .frame(height: 36)
            }

            // Legend
            HStack(spacing: 16) {
                LegendItem(color: LumiColor.calm,     label: "Calme")
                LegendItem(color: LumiColor.primary,  label: "Léger")
                LegendItem(color: LumiColor.movement, label: "Agité")
                LegendItem(color: LumiColor.alert,    label: "Réveil")
            }
        }
    }
}

private struct LegendItem: View {
    let color: Color
    let label: String
    var body: some View {
        HStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 2).fill(color).frame(width: 12, height: 8)
            Text(label).font(LumiFont.caption).foregroundStyle(LumiColor.textSecondary)
        }
    }
}
