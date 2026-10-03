# -*- coding: utf-8 -*-
"""Optional Windows texture converters. Fail visibly; never invoke a shell."""
import os
import subprocess
from pathlib import Path


class TextureConversionError(RuntimeError):
    pass


def conversionArguments(kind, path):
    path = Path(path).resolve()
    executable = Path(__file__).resolve().parent / ("MHWorldTex.exe" if kind == "tex" else "TexConv.exe")
    args = [str(executable), str(path)]
    if kind == "dds":
        if "NM" in path.name:
            args += ["-sepalpha", "-f", "RGBA"]
        args += ["-ft", "png", "-o", str(path.parent)]
    return args


def _convert(kind, path):
    args = conversionArguments(kind, path)
    if not Path(args[0]).is_file():
        raise FileNotFoundError("Texture converter missing: " + args[0])
    if not Path(args[1]).is_file():
        raise FileNotFoundError("Texture input missing: " + args[1])
    if os.name != 'nt':
        raise TextureConversionError("Bundled texture conversion requires Windows; provide PNG textures")
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False, check=True, timeout=120,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.SubprocessError) as exc:
        raise TextureConversionError("Texture conversion failed for %s: %s" % (args[1], exc)) from exc
    output = Path(args[1]).with_suffix('.dds' if kind == 'tex' else '.png')
    if not output.is_file():
        raise TextureConversionError("Converter did not produce expected output: %s; %s" %
                                     (output, result.stderr.decode(errors='replace')))
    return str(output)


def convertTexToDDS(path):
    return _convert('tex', path)


def convertDDSToPNG(path):
    return _convert('dds', path)
