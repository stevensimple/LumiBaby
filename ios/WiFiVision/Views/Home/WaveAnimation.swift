import SwiftUI

struct WaveShape: Shape {
    var phase: Double
    var amplitude: Double = 10
    var frequency: Double = 2.5

    var animatableData: Double {
        get { phase }
        set { phase = newValue }
    }

    func path(in rect: CGRect) -> Path {
        var path = Path()
        let w = Double(rect.width)
        let midY = Double(rect.midY)

        path.move(to: CGPoint(x: 0, y: midY))
        for x in stride(from: 0.0, through: w, by: 1.5) {
            let y = midY + amplitude * sin((x / w) * frequency * .pi * 2 + phase)
            path.addLine(to: CGPoint(x: x, y: y))
        }
        return path
    }
}

struct AnimatedWaves: View {
    let color: Color
    @State private var phase: Double = 0

    var body: some View {
        ZStack {
            WaveShape(phase: phase, amplitude: 12, frequency: 2.0)
                .stroke(color.opacity(0.18), lineWidth: 2.5)
            WaveShape(phase: phase + 1.2, amplitude: 8, frequency: 2.5)
                .stroke(color.opacity(0.12), lineWidth: 2)
            WaveShape(phase: phase + 2.4, amplitude: 5, frequency: 3.0)
                .stroke(color.opacity(0.07), lineWidth: 1.5)
        }
        .onAppear {
            withAnimation(.linear(duration: 5).repeatForever(autoreverses: false)) {
                phase = .pi * 2
            }
        }
    }
}
