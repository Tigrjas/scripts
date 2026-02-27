#!/usr/bin/env bash
# =============================================================================
# setup-tools.sh — Install tools on a new Linux system
# =============================================================================
# HOW TO USE:
#   1. Make executable:  chmod +x setup-tools.sh
#   2. Run as root:      sudo ./setup-tools.sh
#   3. Install specific tools only:
#                        sudo ./setup-tools.sh micro ripgrep
#
# HOW TO ADD A NEW TOOL:
#
#   OPTION A — Simple apt package (most tools):
#     Just add the package name to the APT_TOOLS list below. Done.
#
#   OPTION B — Tool needs special install logic (e.g. curl installer, snap, etc):
#     Add an install_<toolname>() function in the CUSTOM INSTALLERS section,
#     then add the name to the CUSTOM_TOOLS list.
# =============================================================================

set -uo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# ── Root check ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  error "This script must be run as root (use sudo)."
  exit 1
fi

# =============================================================================
#  ✏️  APT_TOOLS — Add any standard apt package name here.
#  No function needed. Just add the name to the list.
# =============================================================================
APT_TOOLS=(
  # editors & terminal tools
  micro
  btop
  git
  # file & search utilities
  # ripgrep
  # fd-find
  # fzf
  # network tools
  # curl
  # wget
  # dev tools
  # git
  # jq
  # system monitoring
  # htop
  # ncdu
)

# =============================================================================
#  ⚙️  CUSTOM_TOOLS — Tools that need special install logic.
#  Add the name here AND write an install_<name>() function below.
# =============================================================================
CUSTOM_TOOLS=(
  # example_tool
)

# =============================================================================
#  CUSTOM INSTALLERS
#  Only needed for tools that can't simply be apt-installed.
#  Each function must be named install_<toolname> (lowercase).
# =============================================================================

# Template — copy this block to add a new custom tool:
#
# install_example_tool() {
#   if command -v example_tool &>/dev/null; then
#     info "example_tool already installed — skipping."; return 0
#   fi
#   info "Installing example_tool..."
#   curl -fsSL https://example.com/install.sh | bash   # or snap, wget, etc.
#   success "example_tool installed."
# }

# =============================================================================
#  ENGINE — You don't need to edit anything below this line.
# =============================================================================

declare -a INSTALLED=()
declare -a SKIPPED=()
declare -a FAILED=()

apt_update_done=false
ensure_apt_updated() {
  if [[ "$apt_update_done" == false ]]; then
    info "Running apt-get update..."
    apt-get update -qq
    apt_update_done=true
  fi
}

install_apt_tool() {
  local pkg="$1"
  if dpkg -s "$pkg" &>/dev/null; then
    info "${pkg}: already installed — skipping."
    SKIPPED+=("$pkg")
    return 0
  fi
  ensure_apt_updated
  info "Installing ${pkg} via apt..."
  if apt-get install -y "$pkg" &>/dev/null; then
    success "${pkg}: installed."
    INSTALLED+=("$pkg")
  else
    error "${pkg}: apt install failed."
    FAILED+=("$pkg")
  fi
}

install_custom_tool() {
  local tool="$1"
  local fn="install_${tool}"
  if declare -f "$fn" > /dev/null; then
    if $fn; then
      [[ " ${SKIPPED[*]} " != *" $tool "* ]] && INSTALLED+=("$tool")
    else
      FAILED+=("$tool")
    fi
  else
    error "No installer function found for custom tool '${tool}'."
    error "Add an install_${tool}() function to the script."
    FAILED+=("$tool")
  fi
}

print_summary() {
  local total=$(( ${#INSTALLED[@]} + ${#SKIPPED[@]} + ${#FAILED[@]} ))
  echo ""
  echo -e "${BOLD}════════════════════════════════════════${RESET}"
  echo -e "${BOLD}  Summary${RESET}"
  echo -e "${BOLD}════════════════════════════════════════${RESET}"
  echo -e "  Total tools processed: ${BOLD}${total}${RESET}"
  echo ""

  if [[ ${#INSTALLED[@]} -gt 0 ]]; then
    echo -e "  ${GREEN}✔ Installed (${#INSTALLED[@]}):${RESET}"
    for t in "${INSTALLED[@]}"; do echo -e "      • $t"; done
    echo ""
  fi

  if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo -e "  ${YELLOW}⊘ Already installed / skipped (${#SKIPPED[@]}):${RESET}"
    for t in "${SKIPPED[@]}"; do echo -e "      • $t"; done
    echo ""
  fi

  if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo -e "  ${RED}✘ Failed (${#FAILED[@]}):${RESET}"
    for t in "${FAILED[@]}"; do echo -e "      • $t"; done
    echo ""
    echo -e "${BOLD}════════════════════════════════════════${RESET}"
    echo -e "${RED}Some tools failed to install. See errors above.${RESET}"
  else
    echo -e "${BOLD}════════════════════════════════════════${RESET}"
    echo -e "${GREEN}All tools processed successfully!${RESET}"
  fi
  echo ""
}

main() {
  echo ""
  echo -e "${BOLD}════════════════════════════════════════${RESET}"
  echo -e "${BOLD}  Linux Tool Setup Script               ${RESET}"
  echo -e "${BOLD}════════════════════════════════════════${RESET}"

  if [[ $# -gt 0 ]]; then
    info "Installing requested tools: $*"
    for tool in "$@"; do
      if [[ " ${CUSTOM_TOOLS[*]} " == *" $tool "* ]]; then
        install_custom_tool "$tool"
      else
        install_apt_tool "$tool"
      fi
    done
  else
    for tool in "${APT_TOOLS[@]}";    do install_apt_tool    "$tool"; done
    for tool in "${CUSTOM_TOOLS[@]}"; do install_custom_tool "$tool"; done
  fi

  print_summary
  [[ ${#FAILED[@]} -eq 0 ]]
}

main "$@"
