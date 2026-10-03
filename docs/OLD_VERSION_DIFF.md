# 旧 4.4.3 版与 upstream 逐文件分析

旧 ZIP 与旧目录完全一致，并非独立原版。没有旧版本 Git 历史，不能把每一处差异都归因于 AI。旧版缺少多个较新 upstream 模块，存在不同基础版本的结构差异。完整原始文本 diff 位于工作区 `audit-artifacts/old-vs-upstream.diff`，本文件记录移植决策。

| 文件 | 原始差异分类 | 移植决策 |
|---|---|---|
| `.gitattributes` | changed | 不整目录移植；采用 upstream，必要问题见审计状态。 |
| `.gitignore` | changed | 不整目录移植；采用 upstream，必要问题见审计状态。 |
| `INSTALLATION_GUIDE.md` | old-only | 旧文档保留参考；重写维护分支测试事实与限制，不继承未经验证的承诺。 |
| `QUICK_FIX.md` | old-only | 旧文档保留参考；重写维护分支测试事实与限制，不继承未经验证的承诺。 |
| `README.md` | changed | 旧文档保留参考；重写维护分支测试事实与限制，不继承未经验证的承诺。 |
| `TROUBLESHOOTING_GUIDE.md` | old-only | 旧文档保留参考；重写维护分支测试事实与限制，不继承未经验证的承诺。 |
| `__init__.py` | changed | 重新实现必要现代注册/annotation/menu APIs；添加生命周期与输出失败检查。 |
| `__pycache__/__init__.cpython-313.pyc` | old-only | 编译缓存，不纳入贡献。 |
| `blender/BlenderMod3Exporter.py` | changed | 以 upstream 为基础审计；非破坏导出、loop 冲突拒绝、材料次序与 bounds 独立修复。 |
| `blender/BlenderMod3Importer.py` | changed | 选择 object/collection/select/UV API 迁移；拒绝启发式 smooth modifier，独立测试 normals。 |
| `blender/BlenderNodesFunctions.py` | upstream-only | 不整目录移植；采用 upstream，必要问题见审计状态。 |
| `blender/BlenderNormals.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `blender/BlenderSupressor.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `boundingbox/boundingBoxCalculations.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `boundingbox/chull.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `boundingbox/linalg.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `boundingbox/msbr.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `boundingbox/mvbb.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `boundingbox/mvbbApprox.py` | upstream-only | 使用 upstream 模块；根据几何证明修正中心、基、半尺寸，未整目录覆盖。 |
| `common/Cstruct.py` | changed | 不整目录移植；采用 upstream，必要问题见审计状态。 |
| `common/FileLike.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `common/crc.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mod3/Matrices.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mod3/Mod3.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3Components.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3DelayedResolutionWeights.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mod3/Mod3ExporterErrorHandler.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3ExporterLayer.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3ImporterLayer.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3Mesh.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3Skeleton.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mod3/Mod3Statistics.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mod3/Mod3VertexBuffers.py` | changed | 拒绝旧八权重 remainder 错误；保留 upstream 并测试高位 flags。 |
| `mod3/ModellingApi.py` | changed | 保留最新 upstream 格式结构；只移植/修复可证明的解析、验证和序列化问题并添加测试。 |
| `mrl3/MHWorldTex.exe` | identical | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mrl3/Mrl3.py` | changed | 保留 upstream 映射和结构；独立修复参数、边界检查与异常可见性。 |
| `mrl3/TexConv.exe` | identical | 不移植格式噪音；相同逻辑保留 upstream。 |
| `mrl3/TextureConverter.py` | changed | 保留 upstream 映射和结构；独立修复参数、边界检查与异常可见性。 |
| `mrl3/maptype.py` | changed | 保留 upstream 映射和结构；独立修复参数、边界检查与异常可见性。 |
| `mrl3/maptypeGenerator.py` | changed | 保留 upstream 映射和结构；独立修复参数、边界检查与异常可见性。 |
| `operators/__pycache__/mod3export.cpython-313.pyc` | old-only | 编译缓存，不纳入贡献。 |
| `operators/__pycache__/mod3import.cpython-313.pyc` | old-only | 编译缓存，不纳入贡献。 |
| `operators/mod3export.py` | changed | 重新实现必要现代注册/annotation/menu APIs；添加生命周期与输出失败检查。 |
| `operators/mod3import.py` | changed | 重新实现必要现代注册/annotation/menu APIs；添加生命周期与输出失败检查。 |
| `operators/mod3properties.py` | upstream-only | 重新实现必要现代注册/annotation/menu APIs；添加生命周期与输出失败检查。 |
| `scripts/tests.py` | line-endings-only | 不移植格式噪音；相同逻辑保留 upstream。 |

可采纳：现代菜单、annotation、collection linking、select/active、显示/armature APIs 的意图。必须重审：normals、权重、骨架、材质节点、格式 headers、bounding boxes。无意义：换行与缓存。不能确认来源：旧版缺失的新模块和大型 maptype 表差异。
