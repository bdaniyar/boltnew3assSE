import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test, { after } from 'node:test';
import ts from 'typescript';
import { availabilityCases } from './fixtures/availability-cases.mjs';

// Transpile the actual application function, never a copied implementation.
// Set FRONTEND_SOURCE_ROOT to run this identical harness against preserved v1.
const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = path.resolve(repository, process.env.FRONTEND_SOURCE_ROOT || '.');
const temporaryDirectory = await mkdtemp(path.join(tmpdir(), 'a3-frontend-logic-'));
after(() => rm(temporaryDirectory, { recursive: true, force: true }));

for (const name of ['time', 'availability']) {
  const fileName = path.join(sourceRoot, 'src', 'utils', `${name}.ts`);
  const source = await readFile(fileName, 'utf8');
  const { outputText, diagnostics } = ts.transpileModule(source, {
    fileName,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
    reportDiagnostics: true,
  });
  assert.equal(diagnostics?.length ?? 0, 0, `Transpilation diagnostics for ${fileName}`);
  await writeFile(path.join(temporaryDirectory, `${name}.mjs`), outputText.replace(/from (['"])\.\/time\1/g, 'from "./time.mjs"'));
}

const { checkAvailability } = await import(pathToFileURL(path.join(temporaryDirectory, 'availability.mjs')));
console.log(`Actual frontend source: ${path.relative(repository, sourceRoot) || '.'}/src/utils/availability.ts`);

function frozenInput(input) {
  return Object.freeze({
    ...input,
    bookings: Object.freeze(input.bookings.map((booking) => Object.freeze({ ...booking }))),
  });
}

for (const { name, input, expected } of availabilityCases) {
  test(name, () => {
    const frozen = frozenInput(input);
    const before = structuredClone(frozen);
    const actual = checkAvailability(frozen);
    assert.equal(typeof actual.available, 'boolean');
    assert.equal(actual.available, expected);
    assert.ok((actual.available ? actual.message : actual.reason)?.trim(), 'Result has understandable feedback');
    assert.deepEqual(frozen, before, 'All input fields and every existing booking stay unchanged');
    console.log(`${name}: expected=${expected ? 'Available' : 'Unavailable'}, actual=${actual.available ? 'Available' : 'Unavailable'}`);
  });
}
