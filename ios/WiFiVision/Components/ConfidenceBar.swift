import SwiftUI

struct ConfidenceBar: View {
    let value: Double
    var label: String = "Confidence"

    private var color: Color {
        if value >= 0.75 { return .green }
        if value >= 0.5 { return .orange }
        return .red
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(label).font(.caption).foregroundStyle(.secondary)
                Spacer()
                Text("\(Int(value * 100))%").font(.caption).foregroundStyle(.secondary)
            }
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 3).fill(Color.secondary.opacity(0.2)).frame(height: 6)
                    RoundedRectangle(cornerRadius: 3).fill(color).frame(width: geo.size.width * value, height: 6)
                }
            }.frame(height: 6)
        }
    }
}
