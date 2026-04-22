import SwiftUI

struct HistoryView: View {
    @StateObject private var vm = HistoryViewModel()
    @State private var selectedTab = 0

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("", selection: $selectedTab) {
                    Text("Presence").tag(0)
                    Text("Movement").tag(1)
                }
                .pickerStyle(.segmented)
                .padding()

                if vm.isLoading {
                    ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List {
                        if selectedTab == 0 {
                            ForEach(Array(vm.presenceHistory.enumerated()), id: \.offset) { _, item in
                                PresenceHistoryRow(item: item, vm: vm)
                            }
                        } else {
                            ForEach(Array(vm.breathingHistory.enumerated()), id: \.offset) { _, item in
                                MovementHistoryRow(item: item, vm: vm)
                            }
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("History")
            .refreshable { await vm.load() }
            .task { await vm.load() }
        }
    }
}

private struct PresenceHistoryRow: View {
    let item: [String: Any]
    let vm: HistoryViewModel
    var body: some View {
        HStack {
            Image(systemName: (item["detected"] as? Bool == true) ? "figure.child.and.lock" : "questionmark.circle")
                .foregroundStyle((item["detected"] as? Bool == true) ? .green : .secondary)
            VStack(alignment: .leading) {
                Text((item["detected"] as? Bool == true) ? "Baby in crib" : "Not detected")
                    .font(.subheadline.bold())
                Text(vm.formatTime(item["timestamp"] as? String ?? ""))
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if let conf = item["confidence"] as? Double {
                Text("\(Int(conf * 100))%").font(.caption).foregroundStyle(.secondary)
            }
        }
    }
}

private struct MovementHistoryRow: View {
    let item: [String: Any]
    let vm: HistoryViewModel

    private func icon(for level: String) -> String {
        switch level {
        case "calm": return "moon.zzz"
        case "light": return "figure.roll"
        case "agitated": return "waveform.path"
        default: return "exclamationmark.triangle"
        }
    }

    private func label(for level: String) -> String {
        switch level {
        case "calm": return "Resting calmly"
        case "light": return "Light movement"
        case "agitated": return "Agitated"
        case "very_agitated": return "Very agitated"
        default: return level
        }
    }

    var body: some View {
        HStack {
            let level = item["level"] as? String ?? "calm"
            Image(systemName: icon(for: level)).foregroundStyle(.blue)
            VStack(alignment: .leading) {
                Text(label(for: level)).font(.subheadline.bold())
                Text(vm.formatTime(item["timestamp"] as? String ?? ""))
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
        }
    }
}
