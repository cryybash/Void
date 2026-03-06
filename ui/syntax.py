# Copyright 2026 Bailey Lane-Beber
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from config.colors import (COLOR_KEYWORD, COLOR_STRING, COLOR_COMMENT,
                           COLOR_NUMBER, COLOR_BUILTIN, COLOR_DECORATOR,
                           COLOR_NORMAL, COLOR_DEFINITION, COLOR_FUNC_NAME,
                           COLOR_MATCH_BOOL)

LANGUAGES = {
    "python": {
        "extensions": [".py"],
        "boolean": [
            "True", "False",
        ],

        "keywords": [
            "and", "as", "assert", "async", "await",
            "break", "continue", "del", "elif", "else",
            "finally", "for", "global", "if",
            "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
            "while", "with", "yield",
        ],
        "definitions": [
            "def", "class", "return", "import", "from", "None", "try", "except",
        ],
        "builtins": [
            "print", "len", "range", "int", "str", "float", "list", "dict",
            "set", "tuple", "bool", "input", "open", "type", "isinstance",
            "enumerate", "zip", "map", "filter", "sorted", "reversed",
            "abs", "max", "min", "sum", "any", "all", "hasattr", "getattr",
            "setattr", "super", "property", "staticmethod", "classmethod",
        ],
        "comment": "#",
        "string_delimiters": ["\"", "'"],
    },
    "c": {
        "extensions": [".c", ".h"],
        "boolean": [
            "true", "false",
        ],
        "keywords": [
            "auto", "break", "case", "const", "continue", "default", "do",
            "else", "enum", "extern", "for", "goto", "if", "inline",
            "register", "restrict", "return", "sizeof", "static", "switch",
            "typedef", "union", "volatile", "while",
            "NULL",
        ],
        "definitions": [
            "struct", "void", "int", "char", "float", "double", "long",
            "short", "unsigned", "signed", "include", "define", "ifdef",
            "ifndef", "endif", "pragma",
        ],
        "builtins": [
            "printf", "scanf", "malloc", "calloc", "realloc", "free",
            "memcpy", "memset", "strlen", "strcmp", "strcpy", "strcat",
            "fopen", "fclose", "fread", "fwrite", "fprintf", "fscanf",
            "exit", "abort", "atoi", "atof", "sizeof",
        ],
        "comment": "//",
        "string_delimiters": ["\"", "'"],
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".hh"],
        "boolean": [
            "true", "false",
        ],

        "keywords": [
            "alignas", "alignof", "auto", "break", "case", "catch", "const",
            "constexpr", "continue", "decltype", "default", "delete", "do",
            "dynamic_cast", "else", "enum", "explicit", "export", "extern",
            "for", "friend", "goto", "if", "inline", "mutable",
            "new", "noexcept", "nullptr", "operator", "private", "protected",
            "public", "register", "reinterpret_cast", "return", "sizeof",
            "static", "static_assert", "static_cast", "switch", "template",
            "this", "throw", "try", "typedef", "typeid", "typename",
            "union", "using", "virtual", "volatile", "while",
        ],
        "definitions": [
            "class", "struct", "namespace", "void", "int", "char", "float",
            "double", "long", "short", "unsigned", "signed", "bool",
            "string", "vector", "map", "set", "include", "define", "ifdef",
            "ifndef", "endif", "pragma",
        ],
        "builtins": [
            "std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "pair", "make_pair", "make_shared", "make_unique",
            "shared_ptr", "unique_ptr", "move", "forward", "swap",
            "sort", "find", "begin", "end", "size", "push_back", "emplace_back",
            "printf", "scanf", "malloc", "free",
        ],
        "comment": "//",
        "string_delimiters": ["\"", "'"],
    },
    "rust": {
        "extensions": [".rs"],
        "boolean": [
            "true", "false",
        ],

        "keywords": [
            "as", "async", "await", "break", "const", "continue", "crate",
            "dyn", "else", "extern", "for", "if", "in",
            "let", "loop", "match", "move", "mut", "pub", "ref",
            "return", "self", "Self", "static", "super",
            "unsafe", "where", "while", "yield",
        ],
        "definitions": [
            "fn", "struct", "enum", "trait", "impl", "mod", "type",
            "use", "macro_rules",
        ],
        "builtins": [
            "println", "print", "eprintln", "eprint", "format", "vec",
            "Box", "Rc", "Arc", "Cell", "RefCell", "Option", "Result",
            "Some", "None", "Ok", "Err", "String", "Vec", "HashMap",
            "HashSet", "BTreeMap", "BTreeSet", "Into", "From", "Clone",
            "Copy", "Debug", "Display", "Default", "Iterator", "IntoIterator",
            "unwrap", "expect", "map", "filter", "collect", "iter",
            "i8", "i16", "i32", "i64", "i128", "isize",
            "u8", "u16", "u32", "u64", "u128", "usize",
            "f32", "f64", "bool", "char", "str",
        ],
        "comment": "//",
        "string_delimiters": ["\""],
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"],
        "boolean": [
            "true", "false",
        ],
        "keywords": [
            "await", "break", "case", "catch", "const", "continue",
            "debugger", "default", "delete", "do", "else", "export",
            "extends", "finally", "for", "if", "implements",
            "import", "in", "instanceof", "interface", "let", "new", "null",
            "of", "package", "private", "protected", "public", "return",
            "static", "super", "switch", "this", "throw", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield",
            "async",
        ],
        "definitions": [
            "function", "class", "from", "import", "export",
        ],
        "builtins": [
            "console", "log", "warn", "error", "info",
            "Math", "JSON", "Object", "Array", "String", "Number",
            "Boolean", "Date", "RegExp", "Map", "Set", "WeakMap", "WeakSet",
            "Promise", "Symbol", "Proxy", "Reflect",
            "parseInt", "parseFloat", "isNaN", "isFinite",
            "setTimeout", "setInterval", "clearTimeout", "clearInterval",
            "fetch", "require", "module", "exports",
            "document", "window", "globalThis",
            "push", "pop", "shift", "unshift", "splice", "slice",
            "map", "filter", "reduce", "forEach", "find", "findIndex",
            "includes", "indexOf", "join", "split", "replace", "match",
            "then", "catch", "finally", "resolve", "reject",
        ],
        "comment": "//",
        "string_delimiters": ["\"", "'", "`"],
    },
}

# from file extension
def detect_language(filename):
    if filename is None:
        return None
        
    for lang, config in LANGUAGES.items():
        for ext in config["extensions"]:
            if filename.endswith(ext):
                return lang
    return None


_NAME_FOLLOWS = {
    "def", "class", "fn", "function", "struct", "enum",
    "trait", "namespace", "mod", "type", "union", "except",
}

def _tokenize_fstring(line, i, quote):
    tokens = [(quote, COLOR_STRING)]  # opening quote
    j = i + 1
    while j < len(line):
        if line[j] == "\\" and j + 1 < len(line):
            tokens.append((line[j:j+2], COLOR_STRING))
            j += 2
            continue
        if line[j] == quote:
            tokens.append((quote, COLOR_STRING))
            j += 1
            break
        if line[j] == "{":
            depth = 1
            k = j + 1
            while k < len(line) and depth > 0:
                if line[k] == "{":
                    depth += 1
                elif line[k] == "}":
                    depth -= 1
                k += 1
            tokens.append(("{", COLOR_KEYWORD))
            tokens.append((line[j+1:k-1], COLOR_NORMAL))
            tokens.append(("}", COLOR_KEYWORD))
            j = k
            continue
        
        str_start = j
        
        while j < len(line) and line[j] != quote and line[j] != "{" and line[j] != "\\":
            j += 1
        tokens.append((line[str_start:j], COLOR_STRING))
    
    return tokens, j

# for syntax highlighting
def tokenize_line(line, lang):
    if lang is None:
        
        return [(line, COLOR_NORMAL)]

    config = LANGUAGES.get(lang)
    
    if config is None:
        
        return [(line, COLOR_NORMAL)]

    tokens = []
    i = 0
    
    # [COMMENTS] - everything from comment char to end of line
    while i < len(line):
        if line[i:].startswith(config["comment"]):
            tokens.append((line[i:], COLOR_COMMENT))
            break
      
                # [F-STRING] 
        if (line[i] == "f" and lang == "python"
                and i + 1 < len(line) and line[i+1] in config["string_delimiters"]
                and (i == 0 or not line[i-1].isalnum() and line[i-1] != "_")):
            tokens.append(("f", COLOR_STRING))
            i += 1
            
            continue

        # [STRINGS]
        if line[i] in config["string_delimiters"]:
            quote = line[i]
            is_fstring = (i > 0 and line[i-1] == "f" and lang == "python")

            if line[i:i+3] == quote * 3:
                end = line.find(quote * 3, i + 3)
                
                if end == -1:
                    tokens.append((line[i:], COLOR_STRING))
                    break
                else:
                    tokens.append((line[i:end+3], COLOR_STRING))
                    i = end + 3
                    continue
            else:
                if not is_fstring:
                    j = i + 1
                    
                    while j < len(line):
                        if line[j] == "\\" and j + 1 < len(line):
                            j += 2
                            continue
                        if line[j] == quote:
                            j += 1
                            
                            break
                        j += 1
                    tokens.append((line[i:j], COLOR_STRING))
                    i = j
                    
                    continue
                else:
                    fstring_tokens, j = _tokenize_fstring(line, i, quote)
                    tokens.extend(fstring_tokens)
                    i = j
                    continue

        # [DECORATORS] / [PREPROCESSOR DIRECTIVES]
        if line[i] == "@" and (i == 0 or line[i-1] in " \t"):
            j = i + 1
            while j < len(line) and (line[j].isalnum() or line[j] in "_."):
                j += 1
            tokens.append((line[i:j], COLOR_DECORATOR))
            i = j
            continue
        if line[i] == "#" and config["comment"] != "#" and (i == 0 or line[i-1] in " \t"):
            j = i + 1
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            tokens.append((line[i:j], COLOR_DECORATOR))
            i = j
            continue

        # [NUMBERS]
        if line[i].isdigit() and (i == 0 or not line[i-1].isalnum()):
            j = i
            while j < len(line) and (line[j].isdigit() or line[j] in ".xXoObB_abcdefABCDEF"):
                j += 1
            tokens.append((line[i:j], COLOR_NUMBER))
            i = j
            continue

        # [WORDS] - check for keywords, definitions, and builtins
        if line[i].isalpha() or line[i] == "_":
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            if word in config["keywords"]:
                tokens.append((word, COLOR_KEYWORD))
            elif word in config.get("definitions", []):
                tokens.append((word, COLOR_DEFINITION))
                
                # this is for coloring the names after a class/function
                if word in _NAME_FOLLOWS:
                    k = j
                    while k < len(line) and line[k] == " ":
                        tokens.append((" ", COLOR_NORMAL))
                        k += 1
                    if k < len(line) and (line[k].isalpha() or line[k] == "_"):
                        name_start = k
                        while k < len(line) and (line[k].isalnum() or line[k] == "_"):
                            k += 1
                        tokens.append((line[name_start:k], COLOR_FUNC_NAME))
                    j = k
            elif word in config["builtins"]:
                tokens.append((word, COLOR_BUILTIN))
            elif word in config["boolean"]:    # NEW 
                tokens.append((word, COLOR_MATCH_BOOL))            
            else:
                tokens.append((word, COLOR_NORMAL))
            i = j
            
            continue

        # ANYTHING ELSE - single character
        tokens.append((line[i], COLOR_NORMAL))
        i += 1
        
    return tokens 




