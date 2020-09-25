#
# Prepare a new release of smart_open.  Use it like this:
#
#     export SMART_OPEN_RELEASE=2.3.4
#     bash release/prepare.sh
#
# where 1.2.3 is the new version to release.
#
# Does the following:
#
# - Creates a clean virtual environment
# - Runs tests
# - Creates a local release git branch
# - Bumps VERSION accordingly
# - Opens CHANGELOG.md for editing, commits updates
#
# Once you're happy, run merge.sh to continue with the release.
#
set -euxo pipefail

version="$SMART_OPEN_RELEASE"
echo "version: $version"

script_dir="$(dirname "${BASH_SOURCE[0]}")"
cd "$script_dir/.."

git fetch upstream

#
# Delete the release branch in case one is left lying around.
#
git checkout upstream/develop
set +e
git branch -D release-"$version"
set -e

git checkout upstream/develop -b release-"$version"
echo "__version__ = '$version'" > smart_open/version.py
git commit smart_open/version.py -m "bump version to $version"

echo "Next, update CHANGELOG.md."
echo "Consider running summarize_pr.sh for each PR merged since the last release."
read -p "Press Enter to continue..."

${EDITOR:-vim} CHANGELOG.md
set +e
git commit CHANGELOG.md -m "updated CHANGELOG.md for version $version"
set -e

echo "Have a look at the current branch, and if all looks good, run merge.sh"
