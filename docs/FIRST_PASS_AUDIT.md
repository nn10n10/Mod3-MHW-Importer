# 第一轮全仓审计（修改前基线）

基线：upstream master `364c2609562436cbbee8dca3a2c91c1a4fe6bc6c`。审计日期：2026-10-03。
报告清单在代码移植前建立；下列行号固定为upstream基线，后续状态另见 FIX_STATUS.md。
完整备份：`C:/Users/owner/Desktop/test-backup-20261003-203935`，39文件SHA-256一致。
同目录ZIP与旧目录所有文件匹配。旧版安装指南写4.4.3、实际4.4.3注册通过，符合用户描述；不据此证明模型输出正确。
旧版来自较老格式结构，不将所有旧版与2.1.0差异归因于AI；未有修改记录证明来源。
全仓Python源码逐文件阅读，大型maptype常量表用AST逐条读取比较。所有exe只做SHA-256比对，没有执行。

严重度：CRITICAL 1 / HIGH 19 / MEDIUM 8 / COMPATIBILITY 5 / LOW 4 / TEST GAP 3。

## C-01

ID：C-01

Severity：CRITICAL

文件：operators/mod3export.py

函数 / 行：cleanScene / 103（修改前基线）

问题：删除其他scene对象

触发条件：多场景导出

为什么是问题：全局删除用户数据

Blender 4.4.3 是否受影响：旧版没有 upstream 的 cleanScene 实现；不按相同全局删除路径判定受影响。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：移除cleanScene

需要什么 regression test：其他scene对象保持

## H-01

ID：H-01

Severity：HIGH

文件：operators/mod3export.py

函数 / 行：execute / 78（修改前基线）

问题：导出transform_apply修改源网格

触发条件：非单位变换/共享mesh

为什么是问题：失败仍留副作用

Blender 4.4.3 是否受影响：是；旧版 operators/mod3export.py:76 仍使用 transform_apply，实际操作会修改源对象。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：临时mesh复制并显式world变换

需要什么 regression test：共享mesh/失败场景快照

## H-02

ID：H-02

Severity：HIGH

文件：blender/BlenderMod3Exporter.py

函数 / 行：MeshClone / 43（修改前基线）

问题：MeshClone立即return导致后续不可达

触发条件：全部导出

为什么是问题：修改源LOD/normals且忽略modifiers

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：启用可清理副本并明确modifier策略

需要什么 regression test：datablock计数及LOD不变

## H-03

ID：H-03

Severity：HIGH

文件：mod3/Mod3Mesh.py

函数 / 行：Mod3MeshCollection.marshall / 294（修改前基线）

问题：吞掉mesh解析错误及bbox不足

触发条件：截断/未知blocktype

为什么是问题：部分模型假成功

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：异常传播及范围验证

需要什么 regression test：截断各section

## H-04

ID：H-04

Severity：HIGH

文件：mod3/Mod3.py

函数 / 行：marshall / 29（修改前基线）

问题：无magic/version/offset/count验证

触发条件：坏文件/极端数量

为什么是问题：越界读取/过量分配/错误几何

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：按文件大小验证区间

需要什么 regression test：巨大count/负值/无material

## H-05

ID：H-05

Severity：HIGH

文件：blender/BlenderMod3Exporter.py

函数 / 行：loopValues/uvValues/colourValues / 486（修改前基线）

问题：按vertex合并不同loop数据

触发条件：UV seam/硬边/切线/颜色冲突

为什么是问题：丢失首项以外数据

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：冲突必须失败；split另作实现

需要什么 regression test：loop conflict不输出文件

## H-06

ID：H-06

Severity：HIGH

文件：common/Cstruct.py

函数 / 行：HalfToFloat/minifloatSerialize / 16（修改前基线）

问题：binary16非正规数/负零/inf/NaN错误

触发条件：极小UV/边界值

为什么是问题：UV静默改变

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：little endian struct e

需要什么 regression test：65536编码及舍入边界

## H-07

ID：H-07

Severity：HIGH

文件：mod3/Mod3Mesh.py

函数 / 行：verify / 142（修改前基线）

问题：verify引用未调用/zip截短/vertex无verify

触发条件：所有construct

为什么是问题：遗漏末尾vertex/face验证

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：逐元素全量验证

需要什么 regression test：最后vertex/face非法

## H-08

ID：H-08

Severity：HIGH

文件：blender/BlenderMod3Exporter.py

函数 / 行：calculateAABB / 251（修改前基线）

问题：AABB center算成extent

触发条件：偏离原点

为什么是问题：包围盒中心错误

Blender 4.4.3 是否受影响：旧版缺少 upstream boundingbox 模块，本模块的公式不能直接归因于旧版。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：改为(min+max)/2

需要什么 regression test：平移bbox中点

## H-09

ID：H-09

Severity：HIGH

文件：boundingbox/mvbbApprox.py

函数 / 行：inputTransform / 130（修改前基线）

问题：OABB full extent被当half extent

触发条件：Calculate导出

为什么是问题：尺寸半径错误

Blender 4.4.3 是否受影响：旧版缺少 upstream boundingbox 模块，本模块的公式不能直接归因于旧版。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：返回half extent

需要什么 regression test：OABB containment

## H-10

ID：H-10

Severity：HIGH

文件：boundingbox/linalg.py

函数 / 行：completeBasis/getDimension/getEigenvectors / 43（修改前基线）

问题：正交基符号错/未调用determinant/eig读行

触发条件：共线共面及任意方向

为什么是问题：奇异基和错误box

Blender 4.4.3 是否受影响：旧版缺少 upstream boundingbox 模块，本模块的公式不能直接归因于旧版。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：正交基/eigh列/容差

需要什么 regression test：0D至3D含重复点

## H-11

ID：H-11

Severity：HIGH

文件：mod3/Mod3ExporterLayer.py

函数 / 行：ExporterSettings.__init__ / 27（修改前基线）

问题：Explicit字符串当bool

触发条件：选择Explicit

为什么是问题：总是重算忽略原box

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：枚举明确比较

需要什么 regression test：两个模式调用

## H-12

ID：H-12

Severity：HIGH

文件：blender/BlenderMod3Exporter.py

函数 / 行：getBoxClass/getLatticeBoxes/boxFromPair / 294（修改前基线）

问题：Explicit函数typo/参数覆盖/非法list方法

触发条件：Explicit导出

为什么是问题：空box或错误

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：正确pair验证及半尺寸

需要什么 regression test：加载再导出bbox一致

## H-13

ID：H-13

Severity：HIGH

文件：mod3/Mod3Skeleton.py

函数 / 行：Mod3BoneMap.fold / 174（修改前基线）

问题：boneFunction负索引/重复覆盖/sentinel冲突

触发条件：非法或重复function/太多bone

为什么是问题：错误remap

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：范围唯一性限制

需要什么 regression test：负值/重复/255界限

## H-14

ID：H-14

Severity：HIGH

文件：blender/BlenderMod3Importer.py

函数 / 行：createNub/BoneGraph / 409（修改前基线）

问题：前向parent递归缺参数/空骨架/cycle

触发条件：前向parent/无root

为什么是问题：失败或递归溢出

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：层级验证/正确递归/空root

需要什么 regression test：前向骨架及cycle

## H-15

ID：H-15

Severity：HIGH

文件：blender/BlenderMod3Exporter.py

函数 / 行：getSkeletalStructure / 184（修改前基线）

问题：仅EmptyTree导出却允许Armature导入

触发条件：动画Armature导出

为什么是问题：骨架丢失或误选empty

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：明确限制与失败；后续独立实现

需要什么 regression test：Armature导出拒绝

## H-16

ID：H-16

Severity：HIGH

文件：mod3/Mod3ExporterLayer.py

函数 / 行：ModelToMod3.execute / 70（修改前基线）

问题：失败返回FINISHED/先打开wb再serialize

触发条件：验证/序列化失败

为什么是问题：虚假成功/覆盖旧输出

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：异常+CANCELLED/原子替换

需要什么 regression test：原文件KEEP不变

## H-17

ID：H-17

Severity：HIGH

文件：blender/BlenderMod3Importer.py

函数 / 行：clearScene / 201（修改前基线）

问题：默认清除全局objects/images

触发条件：导入多scene

为什么是问题：破坏无关数据

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：默认False/仅当前scene/保护共享collection

需要什么 regression test：多scene和image保留

## H-18

ID：H-18

Severity：HIGH

文件：blender/BlenderNodesFunctions.py

函数 / 行：principledSetup / 37（修改前基线）

问题：Principled数字socket

触发条件：4.x/5.x顺序变化

为什么是问题：RMT接错Alpha等参数

Blender 4.4.3 是否受影响：此具体 upstream 材质模块在旧版不存在；旧版简化材质使用 Base Color 名称，并不继承这些 socket index。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：使用官方socket名称

需要什么 regression test：所有BSDF连接断言

## H-19

ID：H-19

Severity：HIGH

文件：old/mod3/Mod3VertexBuffers.py

函数 / 行：Mod3VertexWeightExtended.marshall / 119（修改前基线）

问题：旧版第8权重算1-sum(原始字节)

触发条件：8-weight格式

为什么是问题：漏缩放漏前3权重严重负值

Blender 4.4.3 是否受影响：是；旧版 Mod3VertexBuffers.py:136 使用 sum(self.byteWeights)，八权重余量不正确。upstream 的该式正确。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：不移植旧逻辑

需要什么 regression test：独立packed八权重fixture

## M-01

ID：M-01

Severity：MEDIUM

文件：mrl3/Mrl3.py

函数 / 行：__getitem__/MRL3Material / 129（修改前基线）

问题：MRL3 texIdx边界/缺map默认第一贴图/serialize typo

触发条件：损坏或缺map

为什么是问题：错误纹理或吞异常

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：验证表/边界/缺map失败

需要什么 regression test：真实MRL3+缺map/截断

## M-02

ID：M-02

Severity：MEDIUM

文件：mrl3/TextureConverter.py

函数 / 行：convertTexToDDS/convertDDSToPNG / 25（修改前基线）

问题：exe拼字符串/吞错误/句柄泄漏/Win专用

触发条件：空格/Unicode/缺exe

为什么是问题：转换假成功

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：argv+DEVNULL+可见错误+输出检查

需要什么 regression test：不执行exe的参数及缺文件测试

## M-03

ID：M-03

Severity：MEDIUM

文件：mod3/Mod3ExporterErrorHandler.py

函数 / 行：propertyDefaults/attemptLoadDefaults / 函数/多位置见原文（修改前基线）

问题：类级mutable defaults

触发条件：不同模型连续export

为什么是问题：前个模型默认污染后个

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：deepcopy实例及返回

需要什么 regression test：隔离两个实例

## M-04

ID：M-04

Severity：MEDIUM

文件：mod3/Mod3Components.py

函数 / 行：Mod3Materials.sceneProperties / 98（修改前基线）

问题：material set/sort重排去重

触发条件：重复/非字母顺序

为什么是问题：material IDs变化

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：原序列+原index hint

需要什么 regression test：重复表及ID保持

## M-05

ID：M-05

Severity：MEDIUM

文件：blender/BlenderMod3Exporter.py

函数 / 行：parseMesh / 426（修改前基线）

问题：忽略polygon material_index

触发条件：多材质mesh

为什么是问题：只写一个材质

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：明确拒绝或后续拆分

需要什么 regression test：多材质拒绝

## M-06

ID：M-06

Severity：MEDIUM

文件：mod3/Mod3VertexBuffers.py

函数 / 行：construct / 30（修改前基线）

问题：construct改输入/zip UV无尺寸校验

触发条件：重复construct/少UV

为什么是问题：输入污染/未初始化

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：复制输入/尺寸验证

需要什么 regression test：重复构建和少UV

## M-07

ID：M-07

Severity：MEDIUM

文件：mod3/Mod3Mesh.py

函数 / 行：splitWeightFunction/signedWeightFunction / 197（修改前基线）

问题：Signed/Group/负权重有损及特殊bits/tangent未保留

触发条件：重复负权重/原始切线

为什么是问题：首次输出变化即使A/B稳定

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：明确限制/Slash回归；特殊项待验证

需要什么 regression test：负4/8weight及高2bits

## M-08

ID：M-08

Severity：MEDIUM

文件：blender/BlenderMod3Exporter.py

函数 / 行：weightHandling / 543（修改前基线）

问题：NaN/inf和zero normals无完整验证

触发条件：非有限通道/奇异矩阵

为什么是问题：非法数字入文件

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：是/可能

修复建议：finite检查/zero策略

需要什么 regression test：NaN/inf与zero normal

## K-01

ID：K-01

Severity：COMPATIBILITY

文件：__init__.py

函数 / 行：register/unregister / 26（修改前基线）

问题：INFO菜单和props赋值旧API

触发条件：4/5注册

为什么是问题：upstream实测4.4.3失败

Blender 4.4.3 是否受影响：旧版已迁移主要菜单和 annotation；4.4.3 注册测试通过，但没有覆盖旧版所有重复注册生命周期。 upstream 的相应源码问题独立成立（旧 API 路径可能先报错）。

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：TOPBAR/annotation/对称指针/回滚

需要什么 regression test：register/unregister/reload

## K-02

ID：K-02

Severity：COMPATIBILITY

文件：blender/BlenderMod3Importer.py

函数 / 行：object/armature/UV APIs / 函数/多位置见原文（修改前基线）

问题：link/select/active/update/UV/armature旧API

触发条件：导入骨架及UV

为什么是问题：失败或吞纹理错误

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：逐函数兼容迁移

需要什么 regression test：真实Blender接口

## K-03

ID：K-03

Severity：COMPATIBILITY

文件：blender/BlenderMod3Exporter.py

函数 / 行：loopValues/listMeshes / 486（修改前基线）

问题：auto_smooth/hide/cursor/loop.normal旧API

触发条件：5.x导出

为什么是问题：失败/错误visibility

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：兼容失败或验证缺口；见问题说明

修复建议：corner_normals及visible_get

需要什么 regression test：normal/hidden scene

## K-04

ID：K-04

Severity：COMPATIBILITY

文件：blender/BlenderNodesFunctions.py

函数 / 行：createTexNode/normalSetup/rmtSetup / 14（修改前基线）

问题：node.color_space/RGB旧节点

触发条件：材质导入

为什么是问题：缺材质/错误数据通道

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：兼容失败或验证缺口；见问题说明

修复建议：image.colorspace及Color节点RGB模式

需要什么 regression test：真实节点及颜色空间

## K-05

ID：K-05

Severity：COMPATIBILITY

文件：boundingbox/msbr.py

函数 / 行：module import / 函数/多位置见原文（修改前基线）

问题：numpy.math已不可依赖

触发条件：新版bundled numpy

为什么是问题：整个模块import失败

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：stdlib math

需要什么 regression test：import和3.13检查

## L-01

ID：L-01

Severity：LOW

文件：mod3/ModellingApi.py

函数 / 行：debugger/abstract methods / 7（修改前基线）

问题：个人debug路径/NotImplemented/typo

触发条件：调试抽象方法

为什么是问题：无诊断/TypeError

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：默认禁debug/正确异常

需要什么 regression test：普通Python接口

## L-02

ID：L-02

Severity：LOW

文件：blender/BlenderSupressor.py

函数 / 行：SupressBlenderOps / 4（修改前基线）

问题：进程级stdout关闭/假定FD1

触发条件：嵌套异常/线程

为什么是问题：日志丢失/错误FD

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：不用默认抑制或dup2

需要什么 regression test：恢复stdout

## L-03

ID：L-03

Severity：LOW

文件：boundingbox/boundingBoxCalculations.py

函数 / 行：__main__ diagnostics / 函数/多位置见原文（修改前基线）

问题：研究脚本eval及导入即IO个人路径

触发条件：运行辅助脚本

为什么是问题：任意代码执行/不可移植

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：literal_eval/main guard

需要什么 regression test：仅静态检查研究脚本

## L-04

ID：L-04

Severity：LOW

文件：mod3/Mod3Skeleton.py

函数 / 行：Mod3BoneMap.unfold / 174（修改前基线）

问题：unfold enumerate整数无return/requiredPropeties拼错

触发条件：未用辅助调用

为什么是问题：TypeError/无结果

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：记录dead helper/独立修复

需要什么 regression test：unfold固定map

## T-01

ID：T-01

Severity：TEST GAP

文件：scripts/tests.py

函数 / 行：module body / 函数/多位置见原文（修改前基线）

问题：tests硬路径/随机50死循环/旧参数/shallow比较

触发条件：少于50样本/相同mtime

为什么是问题：误通过或不能运行

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：相同函数需结合old-vs-upstream.diff；删除模块的旧版不受该模块影响

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：兼容失败或验证缺口；见问题说明

修复建议：参数化确定性真实roundtrip

需要什么 regression test：14blocktypes+用户样本

## T-02

ID：T-02

Severity：TEST GAP

文件：repository

函数 / 行：environment / 函数/多位置见原文（修改前基线）

问题：无5.2及当时无真实sample

触发条件：声明fully supported

为什么是问题：静态不能证明运行

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：见问题条件

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：兼容失败或验证缺口；见问题说明

修复建议：明确target/tested区别

需要什么 regression test：5.2exe及游戏样本

## T-03

ID：T-03

Severity：TEST GAP

文件：repository

函数 / 行：distribution / 函数/多位置见原文（修改前基线）

问题：无顶层LICENSE/binary许可未知

触发条件：发布fork

为什么是问题：不能擅自确定全项目许可

Blender 4.4.3 是否受影响：upstream受影响；用户旧版：见问题条件

Blender 5.2 是否受影响：同逻辑风险；API项有官方源码依据，未实机验证

是否可能造成 silent data corruption：否（但可能阻断或破坏诊断）

修复建议：保留第三方声明/维护者确认

需要什么 regression test：人工review

## 官方兼容性依据

5.2 LTS发布及源码：
- https://www.blender.org/press/blender-5-2-lts-release/
- https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/makesrna/intern/rna_mesh.cc
- https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_bsdf_principled.cc
- https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_sepcomb_color.cc
- https://github.com/blender/blender/blob/blender-v5.2-release/build_files/build_environment/cmake/versions.cmake
5.2源码Principled新加Thin Wall，数字索引更加不可靠；命名socket仍存在。Color节点RGB与Red/Green/Blue通过4.4.3运行测试，5.2只有源码检查。5.2 release分支Python依赖3.13；本机普通Python3.13，4.4.3内置3.11.11。Python3.14未测试。
API文档请求被403/402阻断，采用官方release源码补充；不能据此声称全部5.2 API变更已在运行时验证。

## 全文件覆盖清单

- `__init__.py`：已读。
- `blender/BlenderMod3Exporter.py`：已读。
- `blender/BlenderMod3Importer.py`：已读。
- `blender/BlenderNodesFunctions.py`：已读。
- `blender/BlenderNormals.py`：已读。
- `blender/BlenderSupressor.py`：已读。
- `boundingbox/boundingBoxCalculations.py`：已读。
- `boundingbox/chull.py`：已读。
- `boundingbox/linalg.py`：已读。
- `boundingbox/msbr.py`：已读。
- `boundingbox/mvbb.py`：已读。
- `boundingbox/mvbbApprox.py`：已读。
- `common/crc.py`：已读。
- `common/Cstruct.py`：已读。
- `common/FileLike.py`：已读。
- `mod3/Matrices.py`：已读。
- `mod3/Mod3.py`：已读。
- `mod3/Mod3Components.py`：已读。
- `mod3/Mod3DelayedResolutionWeights.py`：已读。
- `mod3/Mod3ExporterErrorHandler.py`：已读。
- `mod3/Mod3ExporterLayer.py`：已读。
- `mod3/Mod3ImporterLayer.py`：已读。
- `mod3/Mod3Mesh.py`：已读。
- `mod3/Mod3Skeleton.py`：已读。
- `mod3/Mod3Statistics.py`：已读。
- `mod3/Mod3VertexBuffers.py`：已读。
- `mod3/ModellingApi.py`：已读。
- `mrl3/maptype.py`：已读。
- `mrl3/maptypeGenerator.py`：已读。
- `mrl3/Mrl3.py`：已读。
- `mrl3/TextureConverter.py`：已读。
- `operators/mod3export.py`：已读。
- `operators/mod3import.py`：已读。
- `operators/mod3properties.py`：已读。
- `scripts/tests.py`：已读。

## 后续样本证据（不是第一轮已有条件）

用户提供5个MOD3和3个MRL3。新增 H-20（HIGH）：MOD3 mesh bbox count与全局table不一致，旧代码吞错导致数据遗漏。
文件：mod3/Mod3Mesh.py / Mod3MeshCollection.marshall（基线300行附近）。触发：arm 0/23、body 60/23、helm与leg 12/195、wst 0/23。
4.4.3及5.2：格式逻辑均受影响；silent corruption：是。修复建议：在格式证据不足时拒绝有损导入，不猜测分配规则。回归：真实文件明确报错且输入哈希不变；需要原始有效bbox映射文件才能验证正常游戏roundtrip。
严格拒绝是安全策略，仍须维护者确认这些旧工具生成文件的兼容语义，不能认定所有文件内容均无效。
