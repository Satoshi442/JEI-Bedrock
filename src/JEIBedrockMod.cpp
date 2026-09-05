#include <jeibedrock/Version.hpp>

// CONFIRMED: <pl/Mod.hpp>, ll::mod::NativeMod, NativeMod::current(), and
// PL_REGISTER_MOD are taken directly from LeviLaunchroid's own documented
// quick-start guide (docs/guide/developer.md) and its reference
// implementation (examples/full-cpp-mod/src/FullCppMod.cpp).
#include <pl/Mod.hpp>

namespace jeibedrock {

// JEIBedrockMod owns the mod's lifecycle. Phase 0 does nothing but prove
// that load/enable/disable/unload are being called correctly by the
// Preloader. No item registry access, no UI, no hooks - see README.
class JEIBedrockMod {
public:
  static JEIBedrockMod &instance() {
    static JEIBedrockMod mod;
    return mod;
  }

  JEIBedrockMod() : mSelf(*ll::mod::NativeMod::current()) {}

  [[nodiscard]] ll::mod::NativeMod &getSelf() const { return mSelf; }

  bool load() {
    auto &self = getSelf();
    self.getLogger().info("Phase 0 initializing");
    self.getLogger().info("load() called - version {} (phase {})", Version, Phase);
    self.getLogger().info("modRoot={}", self.getModDir().string());
    self.getLogger().info("configDir={}", self.getConfigDir().string());
    self.getLogger().info("resourceDir={}", self.getResourceDir().string());
    self.getLogger().info("Native library loaded");
    return true;
  }

  bool enable() {
    getSelf().getLogger().info("enable() called - mod is now active");
    getSelf().getLogger().info("Phase 0 initialization complete");
    return true;
  }

  bool disable() {
    getSelf().getLogger().info("disable() called - mod is now inactive");
    return true;
  }

  bool unload() {
    getSelf().getLogger().info("unload() called");
    return true;
  }

private:
  ll::mod::NativeMod &mSelf;
};

} // namespace jeibedrock

PL_REGISTER_MOD(jeibedrock::JEIBedrockMod, jeibedrock::JEIBedrockMod::instance())
