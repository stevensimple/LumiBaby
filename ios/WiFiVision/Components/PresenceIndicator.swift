import SwiftUI

struct PresenceIndicator: View {
    let detected: Bool
    let confidence: Double
    @State private var pulse = false

    var body: some View {
        ZStack {
            if detected {
                Circle()
                    .stroke(Color.green.opacity(0.3), lineWidth: 12)
                    .scaleEffect(pulse ? 1.15 : 1.0)
                    .animation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true), value: pulse)
            }
            Circle()
                .fill(detected ? Color.green : Color.secondary.opacity(0.3))
                .frame(width: 20, height: 20)
        }
        .onAppear { pulse = detected }
        .onChange(of: detected) { newValue in pulse = newValue }
    }
}
