# 剩余异常与研究代码清单

以下命中逐项静态复查。保留的 import fallback 和研究函数不等于运行验证；此清单不把每个 except 都等同于 bug。生产修改中的清理后 re-raise 与可选材质错误日志是有意处理。剩余 bare import fallback 会掩盖内部导入错误，旧调试函数/研究脚本仍有可维护性风险。见 FIRST_PASS_AUDIT 与 FIX_STATUS。

| 文件/行 | 命中 |
|---|---|
| `__init__.py:44` | `except Exception:` |
| `blender/BlenderMod3Exporter.py:27` | `except:` |
| `blender/BlenderMod3Exporter.py:64` | `except Exception:` |
| `blender/BlenderMod3Exporter.py:246` | `except:` |
| `blender/BlenderMod3Importer.py:23` | `except:` |
| `blender/BlenderMod3Importer.py:233` | `except Exception as e:` |
| `blender/BlenderMod3Importer.py:278` | `except Exception as e:` |
| `blender/BlenderMod3Importer.py:284` | `except Exception as e:` |
| `blender/BlenderMod3Importer.py:492` | `except:` |
| `boundingbox/boundingBoxCalculations.py:17` | `except:` |
| `boundingbox/boundingBoxCalculations.py:54` | `points = [Vector(eval(line.replace("\\n",""))) for line in outf]` |
| `boundingbox/boundingBoxCalculations.py:84` | `points = [Vector(eval(line.replace("\n",""))) for line in outf]` |
| `boundingbox/boundingBoxCalculations.py:177` | `#except:` |
| `boundingbox/boundingBoxCalculations.py:184` | `modellist = list(Path(r"E:\MHW\chunkG0").rglob("*.mod3"))` |
| `boundingbox/boundingBoxCalculations.py:185` | `#modellist = [Path(r"E:\MHW\chunkG0\Assets\stage\stm410\stm410_018_00\stm410_018_00.mod3")]` |
| `boundingbox/boundingBoxCalculations.py:199` | `#except Exception as e:` |
| `boundingbox/chull.py:26` | `except:` |
| `boundingbox/mvbb.py:7` | `except:` |
| `boundingbox/mvbbApprox.py:18` | `except:` |
| `common/Cstruct.py:162` | `except:` |
| `mod3/Matrices.py:9` | `except:` |
| `mod3/Matrices.py:161` | `except:` |
| `mod3/Mod3.py:12` | `except:` |
| `mod3/Mod3.py:214` | `#with open(r"G:\Wisdom\modelData.txt","w") as outf:` |
| `mod3/Mod3.py:226` | `#modelf = Path(r"E:\MHW\chunkG0\accessory\askill\askill001\mod\common\askill_mantle001.mod3")` |
| `mod3/Mod3.py:252` | `except:` |
| `mod3/Mod3Components.py:11` | `except:` |
| `mod3/Mod3ExporterErrorHandler.py:270` | `except:` |
| `mod3/Mod3ExporterLayer.py:15` | `except:` |
| `mod3/Mod3ExporterLayer.py:55` | `except:` |
| `mod3/Mod3ImporterLayer.py:12` | `except:` |
| `mod3/Mod3Mesh.py:12` | `except:` |
| `mod3/Mod3Skeleton.py:12` | `except:` |
| `mod3/Mod3Statistics.py:57` | `#output = open(r'G:\Wisdom\BitInsanity.txt', 'w')` |
| `mod3/Mod3Statistics.py:61` | `base = r"G:\Mod3ExporterTests"` |
| `mod3/Mod3Statistics.py:63` | `chunkPath = r"E:\MHW\Merged"` |
| `mod3/Mod3Statistics.py:64` | `nativePC = Path(r"E:\Program Files (x86)\Steam\steamapps\common\Monster Hunter World\nativePC")` |
| `mod3/Mod3Statistics.py:80` | `btype = open(r"G:\Wisdom\blocktypes.txt","w")` |
| `mod3/Mod3VertexBuffers.py:10` | `except:` |
| `mod3/Mod3VertexBuffers.py:20` | `except:` |
| `mod3/ModellingApi.py:16` | `except:` |
| `mod3/ModellingApi.py:32` | `raise NotImplemented` |
| `mod3/ModellingApi.py:35` | `raise NotImplemented` |
| `mod3/ModellingApi.py:38` | `raise NotImplemented` |
| `mod3/ModellingApi.py:41` | `raise NotImplemented` |
| `mod3/ModellingApi.py:44` | `raise NotImplemented` |
| `mod3/ModellingApi.py:47` | `raise NotImplemented` |
| `mod3/ModellingApi.py:50` | `raise NotImplemented` |
| `mod3/ModellingApi.py:53` | `raise NotImplemented` |
| `mod3/ModellingApi.py:56` | `raise NotImplemented` |
| `mod3/ModellingApi.py:59` | `raise NotImplemented` |
| `mrl3/Mrl3.py:14` | `except:` |
| `mrl3/Mrl3.py:159` | `except:` |
| `mrl3/TextureConverter.py:32` | `result = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,` |
| `mrl3/TextureConverter.py:33` | `stderr=subprocess.PIPE, shell=False, check=True, timeout=120,` |
| `mrl3/TextureConverter.py:35` | `except (OSError, subprocess.SubprocessError) as exc:` |
