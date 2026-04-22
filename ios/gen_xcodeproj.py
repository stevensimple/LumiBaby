#!/usr/bin/env python3
"""Generate LumiBaby.xcodeproj/project.pbxproj"""
import hashlib, os

def U(seed):
    return hashlib.md5(seed.encode()).hexdigest().upper()[:24]

IOS_DIR = "/Users/steven/Documents/    WiFiVision/ios"
XCODEPROJ = os.path.join(IOS_DIR, "LumiBaby.xcodeproj")
os.makedirs(XCODEPROJ, exist_ok=True)

# ── UUIDs ──────────────────────────────────────────────────────────────
P   = U("lumibaby_project")
TGT = U("lumibaby_target")
APP = U("lumibaby_product_app")

PHASES = {
    "sources":    U("lumibaby_phase_sources"),
    "frameworks": U("lumibaby_phase_frameworks"),
    "resources":  U("lumibaby_phase_resources"),
}
CONFIGS = {
    "proj_debug":   U("lumibaby_proj_debug"),
    "proj_release": U("lumibaby_proj_release"),
    "tgt_debug":    U("lumibaby_tgt_debug"),
    "tgt_release":  U("lumibaby_tgt_release"),
    "proj_list":    U("lumibaby_proj_configlist"),
    "tgt_list":     U("lumibaby_tgt_configlist"),
}
GU = {k: U(f"lumibaby_group_{k}") for k in [
    "main","wifivision","components","design","models",
    "services","viewmodels","views",
    "v_alerts","v_auth","v_calibration","v_history",
    "v_home","v_sensors","v_settings","v_sleep","products"
]}

# ── Files: (filename, path_from_srcroot, group_key) ────────────────────
FILES = [
    ("WiFiVisionApp.swift",        "WiFiVision/WiFiVisionApp.swift",                    "wifivision"),
    ("ConfidenceBar.swift",        "WiFiVision/Components/ConfidenceBar.swift",          "components"),
    ("PresenceIndicator.swift",    "WiFiVision/Components/PresenceIndicator.swift",      "components"),
    ("StatusBadge.swift",          "WiFiVision/Components/StatusBadge.swift",            "components"),
    ("LumiTheme.swift",            "WiFiVision/Design/LumiTheme.swift",                  "design"),
    ("Alert.swift",                "WiFiVision/Models/Alert.swift",                      "models"),
    ("CalibrationState.swift",     "WiFiVision/Models/CalibrationState.swift",           "models"),
    ("RoomStatus.swift",           "WiFiVision/Models/RoomStatus.swift",                 "models"),
    ("Sensor.swift",               "WiFiVision/Models/Sensor.swift",                     "models"),
    ("SleepModels.swift",          "WiFiVision/Models/SleepModels.swift",                "models"),
    ("APIService.swift",           "WiFiVision/Services/APIService.swift",               "services"),
    ("AuthService.swift",          "WiFiVision/Services/AuthService.swift",              "services"),
    ("WebSocketService.swift",     "WiFiVision/Services/WebSocketService.swift",         "services"),
    ("AlertsViewModel.swift",      "WiFiVision/ViewModels/AlertsViewModel.swift",        "viewmodels"),
    ("CalibrationViewModel.swift", "WiFiVision/ViewModels/CalibrationViewModel.swift",   "viewmodels"),
    ("HistoryViewModel.swift",     "WiFiVision/ViewModels/HistoryViewModel.swift",       "viewmodels"),
    ("HomeViewModel.swift",        "WiFiVision/ViewModels/HomeViewModel.swift",          "viewmodels"),
    ("SensorsViewModel.swift",     "WiFiVision/ViewModels/SensorsViewModel.swift",       "viewmodels"),
    ("SleepViewModel.swift",       "WiFiVision/ViewModels/SleepViewModel.swift",         "viewmodels"),
    ("AlertsView.swift",           "WiFiVision/Views/Alerts/AlertsView.swift",           "v_alerts"),
    ("LoginView.swift",            "WiFiVision/Views/Auth/LoginView.swift",              "v_auth"),
    ("CalibrationView.swift",      "WiFiVision/Views/Calibration/CalibrationView.swift", "v_calibration"),
    ("HistoryView.swift",          "WiFiVision/Views/History/HistoryView.swift",         "v_history"),
    ("HomeView.swift",             "WiFiVision/Views/Home/HomeView.swift",               "v_home"),
    ("WaveAnimation.swift",        "WiFiVision/Views/Home/WaveAnimation.swift",          "v_home"),
    ("SensorsView.swift",          "WiFiVision/Views/Sensors/SensorsView.swift",         "v_sensors"),
    ("SettingsView.swift",         "WiFiVision/Views/Settings/SettingsView.swift",       "v_settings"),
    ("SleepTimelineView.swift",    "WiFiVision/Views/Sleep/SleepTimelineView.swift",     "v_sleep"),
    ("SleepView.swift",            "WiFiVision/Views/Sleep/SleepView.swift",             "v_sleep"),
]

FR  = {rel: U(f"lumibaby_ref_{rel}")   for _, rel, _ in FILES}
BF  = {rel: U(f"lumibaby_build_{rel}") for _, rel, _ in FILES}

# ── Group children ─────────────────────────────────────────────────────
gc = {k: [] for k in GU}
for child, parent in {
    "wifivision":"main","components":"wifivision","design":"wifivision",
    "models":"wifivision","services":"wifivision","viewmodels":"wifivision",
    "views":"wifivision","v_alerts":"views","v_auth":"views",
    "v_calibration":"views","v_history":"views","v_home":"views",
    "v_sensors":"views","v_settings":"views","v_sleep":"views",
    "products":"main",
}.items():
    gc[parent].append(GU[child])
for fname, rel, gkey in FILES:
    gc[gkey].append(FR[rel])
gc["products"].append(APP)

# ── Group metadata ─────────────────────────────────────────────────────
GROUP_NAME = {
    "main":"LumiBaby","wifivision":"WiFiVision","components":"Components",
    "design":"Design","models":"Models","services":"Services",
    "viewmodels":"ViewModels","views":"Views","v_alerts":"Alerts",
    "v_auth":"Auth","v_calibration":"Calibration","v_history":"History",
    "v_home":"Home","v_sensors":"Sensors","v_settings":"Settings",
    "v_sleep":"Sleep","products":"Products",
}
GROUP_PATH = {
    "wifivision":"WiFiVision","components":"Components","design":"Design",
    "models":"Models","services":"Services","viewmodels":"ViewModels",
    "views":"Views","v_alerts":"Alerts","v_auth":"Auth",
    "v_calibration":"Calibration","v_history":"History","v_home":"Home",
    "v_sensors":"Sensors","v_settings":"Settings","v_sleep":"Sleep",
}

# ── Build the pbxproj ──────────────────────────────────────────────────
L = []
w = L.append

w("// !$*UTF8*$!")
w("{")
w("\tarchiveVersion = 1;")
w("\tclasses = {")
w("\t};")
w("\tobjectVersion = 56;")
w("\tobjects = {")

# PBXBuildFile
w("\n/* Begin PBXBuildFile section */")
for fname, rel, _ in FILES:
    w(f"\t\t{BF[rel]} /* {fname} in Sources */ = {{isa = PBXBuildFile; fileRef = {FR[rel]} /* {fname} */; }};")
w("/* End PBXBuildFile section */")

# PBXFileReference
w("\n/* Begin PBXFileReference section */")
w(f"\t\t{APP} /* LumiBaby.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = LumiBaby.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
for fname, rel, _ in FILES:
    w(f"\t\t{FR[rel]} /* {fname} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {fname}; sourceTree = \"<group>\"; }};")
w("/* End PBXFileReference section */")

# PBXFrameworksBuildPhase
w("\n/* Begin PBXFrameworksBuildPhase section */")
w(f"\t\t{PHASES['frameworks']} /* Frameworks */ = {{")
w(f"\t\t\tisa = PBXFrameworksBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (\n\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")
w("/* End PBXFrameworksBuildPhase section */")

# PBXGroup
w("\n/* Begin PBXGroup section */")
for gkey, guuid in GU.items():
    name = GROUP_NAME[gkey]
    w(f"\t\t{guuid} /* {name} */ = {{")
    w(f"\t\t\tisa = PBXGroup;")
    w(f"\t\t\tchildren = (")
    for child in gc[gkey]:
        w(f"\t\t\t\t{child},")
    w(f"\t\t\t);")
    if gkey in GROUP_PATH:
        w(f"\t\t\tpath = {GROUP_PATH[gkey]};")
    else:
        w(f"\t\t\tname = {name};")
    w(f"\t\t\tsourceTree = \"<group>\";")
    w(f"\t\t}};")
w("/* End PBXGroup section */")

# PBXNativeTarget
w("\n/* Begin PBXNativeTarget section */")
w(f"\t\t{TGT} /* LumiBaby */ = {{")
w(f"\t\t\tisa = PBXNativeTarget;")
w(f"\t\t\tbuildConfigurationList = {CONFIGS['tgt_list']};")
w(f"\t\t\tbuildPhases = (")
w(f"\t\t\t\t{PHASES['sources']} /* Sources */,")
w(f"\t\t\t\t{PHASES['frameworks']} /* Frameworks */,")
w(f"\t\t\t\t{PHASES['resources']} /* Resources */,")
w(f"\t\t\t);")
w(f"\t\t\tbuildRules = (\n\t\t\t);")
w(f"\t\t\tdependencies = (\n\t\t\t);")
w(f"\t\t\tname = LumiBaby;")
w(f"\t\t\tproductName = LumiBaby;")
w(f"\t\t\tproductReference = {APP} /* LumiBaby.app */;")
w(f"\t\t\tproductType = \"com.apple.product-type.application\";")
w(f"\t\t}};")
w("/* End PBXNativeTarget section */")

# PBXProject
w("\n/* Begin PBXProject section */")
w(f"\t\t{P} /* Project object */ = {{")
w(f"\t\t\tisa = PBXProject;")
w(f"\t\t\tattributes = {{")
w(f"\t\t\t\tBuildIndependentTargetsInParallel = 1;")
w(f"\t\t\t\tLastSwiftUpdateCheck = 1530;")
w(f"\t\t\t\tLastUpgradeCheck = 1530;")
w(f"\t\t\t\tTargetAttributes = {{")
w(f"\t\t\t\t\t{TGT} = {{")
w(f"\t\t\t\t\t\tCreatedOnToolsVersion = 15.3;")
w(f"\t\t\t\t\t}};")
w(f"\t\t\t\t}};")
w(f"\t\t\t}};")
w(f"\t\t\tbuildConfigurationList = {CONFIGS['proj_list']};")
w(f"\t\t\tcompatibilityVersion = \"Xcode 14.0\";")
w(f"\t\t\tdevelopmentRegion = fr;")
w(f"\t\t\thasScannedForEncodings = 0;")
w(f"\t\t\tknownRegions = (fr, en, Base);")
w(f"\t\t\tmainGroup = {GU['main']} /* LumiBaby */;")
w(f"\t\t\tproductRefGroup = {GU['products']} /* Products */;")
w(f"\t\t\tprojectDirPath = \"\";")
w(f"\t\t\tprojectRoot = \"\";")
w(f"\t\t\ttargets = (\n\t\t\t\t{TGT} /* LumiBaby */,\n\t\t\t);")
w(f"\t\t}};")
w("/* End PBXProject section */")

# PBXResourcesBuildPhase
w("\n/* Begin PBXResourcesBuildPhase section */")
w(f"\t\t{PHASES['resources']} /* Resources */ = {{")
w(f"\t\t\tisa = PBXResourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (\n\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")
w("/* End PBXResourcesBuildPhase section */")

# PBXSourcesBuildPhase
w("\n/* Begin PBXSourcesBuildPhase section */")
w(f"\t\t{PHASES['sources']} /* Sources */ = {{")
w(f"\t\t\tisa = PBXSourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
for fname, rel, _ in FILES:
    w(f"\t\t\t\t{BF[rel]} /* {fname} in Sources */,")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")
w("/* End PBXSourcesBuildPhase section */")

# XCBuildConfiguration
w("\n/* Begin XCBuildConfiguration section */")
PROJ_COMMON = [
    "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;",
    "\t\t\t\tCLANG_ANALYZER_NONNULL = YES;",
    "\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = \"gnu++20\";",
    "\t\t\t\tCLANG_ENABLE_MODULES = YES;",
    "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;",
    "\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;",
    "\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;",
    "\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;",
    "\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;",
    "\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;",
    "\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;",
    "\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;",
    "\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;",
    "\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;",
    "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 16.0;",
    "\t\t\t\tMTL_FAST_MATH = YES;",
    "\t\t\t\tSDKROOT = iphoneos;",
]
TGT_COMMON = [
    "\t\t\t\tCODE_SIGN_STYLE = Automatic;",
    "\t\t\t\tCURRENT_PROJECT_VERSION = 1;",
    "\t\t\t\tGENERATE_INFOPLIST_FILE = YES;",
    "\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = LumiBaby;",
    "\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = NO;",
    "\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;",
    "\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;",
    "\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = UIInterfaceOrientationPortrait;",
    "\t\t\t\tMARKETING_VERSION = 1.0;",
    "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.lumibaby.app;",
    "\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";",
    "\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;",
    "\t\t\t\tSWIFT_STRICT_CONCURRENCY = minimal;",
    "\t\t\t\tSWIFT_VERSION = 5.0;",
    "\t\t\t\tTARGETED_DEVICE_FAMILY = 1;",
]

for ckey, cname, extra_lines in [
    (CONFIGS["proj_debug"],   "Debug",   [
        "\t\t\t\tCOPY_PHASE_STRIP = NO;",
        "\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;",
        "\t\t\t\tENABLE_TESTABILITY = YES;",
        "\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;",
        "\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;",
        "\t\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (\"DEBUG=1\", \"$(inherited)\");",
        "\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;",
        "\t\t\t\tONLY_ACTIVE_ARCH = YES;",
        "\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = \"DEBUG $(inherited)\";",
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-Onone\";",
    ]),
    (CONFIGS["proj_release"], "Release", [
        "\t\t\t\tDEBUG_INFORMATION_FORMAT = \"dwarf-with-dsym\";",
        "\t\t\t\tENABLE_NS_ASSERTIONS = NO;",
        "\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;",
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-O\";",
        "\t\t\t\tVALIDATE_PRODUCT = YES;",
    ]),
]:
    w(f"\t\t{ckey} /* {cname} */ = {{")
    w(f"\t\t\tisa = XCBuildConfiguration;")
    w(f"\t\t\tbuildSettings = {{")
    for line in PROJ_COMMON + extra_lines:
        w(line)
    w(f"\t\t\t}};")
    w(f"\t\t\tname = {cname};")
    w(f"\t\t}};")

for ckey, cname, extra_lines in [
    (CONFIGS["tgt_debug"],   "Debug",   [
        "\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = \"DEBUG $(inherited)\";",
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-Onone\";",
    ]),
    (CONFIGS["tgt_release"], "Release", [
        "\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;",
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-O\";",
    ]),
]:
    w(f"\t\t{ckey} /* {cname} */ = {{")
    w(f"\t\t\tisa = XCBuildConfiguration;")
    w(f"\t\t\tbuildSettings = {{")
    for line in TGT_COMMON + extra_lines:
        w(line)
    w(f"\t\t\t}};")
    w(f"\t\t\tname = {cname};")
    w(f"\t\t}};")

w("/* End XCBuildConfiguration section */")

# XCConfigurationList
w("\n/* Begin XCConfigurationList section */")
w(f"\t\t{CONFIGS['proj_list']} /* Build configuration list for PBXProject \"LumiBaby\" */ = {{")
w(f"\t\t\tisa = XCConfigurationList;")
w(f"\t\t\tbuildConfigurations = ({CONFIGS['proj_debug']} /* Debug */, {CONFIGS['proj_release']} /* Release */);")
w(f"\t\t\tdefaultConfigurationIsVisible = 0;")
w(f"\t\t\tdefaultConfigurationName = Release;")
w(f"\t\t}};")
w(f"\t\t{CONFIGS['tgt_list']} /* Build configuration list for PBXNativeTarget \"LumiBaby\" */ = {{")
w(f"\t\t\tisa = XCConfigurationList;")
w(f"\t\t\tbuildConfigurations = ({CONFIGS['tgt_debug']} /* Debug */, {CONFIGS['tgt_release']} /* Release */);")
w(f"\t\t\tdefaultConfigurationIsVisible = 0;")
w(f"\t\t\tdefaultConfigurationName = Release;")
w(f"\t\t}};")
w("/* End XCConfigurationList section */")

w("\t};")
w(f"\trootObject = {P} /* Project object */;")
w("}")

out = os.path.join(XCODEPROJ, "project.pbxproj")
with open(out, "w") as f:
    f.write("\n".join(L) + "\n")
print(f"✓ {out}  ({len(L)} lines)")
