import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import ts from 'typescript';

// Compile the real relative-import graph into an isolated temporary directory.
// Production functions/data are imported; no algorithm is copied into this loader.
export async function loadTypeScriptModules(repository, entryFiles) {
  const temporaryDirectory = await mkdtemp(path.join(tmpdir(), 'a4-production-tests-'));
  const compiled = new Set();

  async function compile(relativeFile) {
    const normalized = path.normalize(relativeFile);
    if (compiled.has(normalized)) return;
    compiled.add(normalized);
    const sourceFile = path.join(repository, normalized);
    const source = await readFile(sourceFile, 'utf8');
    const { outputText, diagnostics } = ts.transpileModule(source, {
      fileName: sourceFile,
      compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
      reportDiagnostics: true,
    });
    assert.equal(diagnostics?.length ?? 0, 0, `Transpilation diagnostics for ${normalized}`);
    const dependencies = [];
    const output = outputText.replace(/\bfrom\s+(['"])(\.[^'"]+)\1/g, (match, quote, specifier) => {
      const dependency = path.normalize(path.join(path.dirname(normalized), specifier));
      const inputFile = /\.ts$/.test(dependency) ? dependency : `${dependency}.ts`;
      dependencies.push(inputFile);
      return `from ${quote}${specifier.replace(/\.ts$/, '')}.mjs${quote}`;
    });
    const targetFile = path.join(temporaryDirectory, normalized.replace(/\.ts$/, '.mjs'));
    await mkdir(path.dirname(targetFile), { recursive: true });
    await writeFile(targetFile, output);
    for (const dependency of dependencies) await compile(dependency);
  }

  try {
    for (const entry of entryFiles) await compile(entry);
    const modules = {};
    for (const entry of entryFiles) {
      modules[entry] = await import(pathToFileURL(path.join(temporaryDirectory, entry.replace(/\.ts$/, '.mjs'))));
    }
    return { modules, cleanup: () => rm(temporaryDirectory, { recursive: true, force: true }) };
  } catch (error) {
    await rm(temporaryDirectory, { recursive: true, force: true });
    throw error;
  }
}
