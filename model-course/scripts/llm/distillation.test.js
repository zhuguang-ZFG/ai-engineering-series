import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import api from "./distillation.cjs";

const fixture = JSON.parse(readFileSync(new URL("../../book/llm/fixtures/distillation.json", import.meta.url), "utf8"));
const near = (actual, expected, tolerance = 1e-8) => assert.ok(Math.abs(actual - expected) < tolerance, `${actual} != ${expected}`);

test("distillation gradient matches finite differences of hard and soft mixed losses", () => {
  const student = [0.4, -0.2, 0.7];
  for (const temperature of [1, 2, 5]) for (const alpha of [0, 0.7, 1]) {
    const result = api.evaluate(fixture.teacher, student, temperature, alpha, 0);
    student.forEach((_, index) => {
      const plus = [...student], minus = [...student];
      plus[index] += 1e-5; minus[index] -= 1e-5;
      const numerical = (api.evaluate(fixture.teacher, plus, temperature, alpha, 0).loss - api.evaluate(fixture.teacher, minus, temperature, alpha, 0).loss) / 2e-5;
      near(result.gradient[index], numerical);
    });
    near(result.teacher.reduce((a, b) => a + b), 1);
    near(result.gradient.reduce((a, b) => a + b), 0);
  }
});

test("student learns a fixed teacher distribution without mutating the teacher or initial student", () => {
  const teacher = [...fixture.teacher], initial = [...fixture.student];
  let student = [...initial];
  const before = api.evaluate(teacher, student, 2, 1, 0);
  for (let i = 0; i < 100; i++) student = api.step(teacher, student, 2, 1, 0).logits;
  const after = api.evaluate(teacher, student, 2, 1, 0);
  assert.ok(after.kl < before.kl / 100);
  assert.ok(after.student[1] > after.student[2]);
  assert.deepEqual(teacher, fixture.teacher);
  assert.deepEqual(initial, fixture.student);
  near(api.evaluate(teacher, teacher, 2, 1, 0).kl, 0);
});

test("a wrong soft teacher can oppose the verified hard label; alpha zero ignores teacher", () => {
  const before = api.evaluate(fixture.wrongTeacher, fixture.student, 2, 0.7, 0);
  const after = api.step(fixture.wrongTeacher, fixture.student, 2, 0.7, 0).after;
  assert.ok(after.inference[0] < before.inference[0]);
  assert.ok(after.inference[1] > before.inference[1]);
  assert.deepEqual(api.evaluate(fixture.teacher, fixture.student, 2, 0, 0).gradient, api.evaluate(fixture.wrongTeacher, fixture.student, 2, 0, 0).gradient);
  for (const temperature of [0, -1, Infinity, NaN]) assert.throws(() => api.evaluate(fixture.teacher, fixture.student, temperature), RangeError);
  assert.throws(() => api.evaluate([1, 2], [1, 2, 3]), RangeError);
  assert.throws(() => api.evaluate([1, NaN], [1, 2]), RangeError);
  assert.throws(() => api.evaluate(fixture.teacher, fixture.student, 2, 1.1), RangeError);
  assert.throws(() => api.step(fixture.teacher, fixture.student, 2, 0.7, 0, -0.1), RangeError);
});
