# Third-party dependencies and source scope

The root MIT license applies to CueAudit code and public workspace documents.
It does not replace the licenses of external software, model services or datasets.
This source repository does not bundle dependency source trees, binary wheels,
models or datasets. Dependencies are installed separately by the user.

| Component | Relationship | Upstream licensing reference |
| --- | --- | --- |
| NumPy | Optional image-measurement dependency | [BSD 3-Clause terms](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| Pillow | Optional image-loading dependency | [Pillow/PIL terms, MIT-CMU](https://github.com/python-pillow/Pillow/blob/main/LICENSE) |
| opencv-python-headless | Optional image-processing dependency | [Python packaging MIT terms](https://github.com/opencv/opencv-python/blob/4.x/LICENSE.txt), [OpenCV Apache 2.0 terms](https://github.com/opencv/opencv/blob/4.x/LICENSE) |
| OpenClaw | Separately installed optional agent runtime | [Upstream MIT license](https://github.com/openclaw/openclaw/blob/main/LICENSE) |

Consult the license files included with the exact versions you install. Binary
distributions can include additional components and notices. OpenClaw is not a
vendored part of CueAudit, and its installed runtime may carry an earlier
copyright notice than the current upstream branch.

## Curated local source

The extraction map in [release scope](docs/release-scope.md) identifies the local
screening scripts and role instructions used for this release. Inspection of the
selected source files found no explicit third-party copyright, license or copied
source attribution identifying a separate license for the extracted functions.
This is a bounded source-notice check, not proof of independent authorship of
every historical local script. The maintainers confirmed MIT for the project.
Any subsequently identified third-party source must retain its applicable notice.

Public workspaces contain newly written operational templates and selected
method-specific instructions. Generic OpenClaw workspace boilerplate, private
session routing, memories and user profiles were not copied into the release.
Runtime interfaces were checked against the installed CLI/documentation; the
adapter does not embed OpenClaw implementation code.
