// Child processes for exercising the upstream hook runner; never invokes a model.
const behavior = process.argv[2];
process.stdin.resume();
process.stdin.on('end', () => {
  if (behavior === 'deny-json') {
    console.log(JSON.stringify({hookSpecificOutput: {permissionDecision: 'deny', permissionDecisionReason: 'fixture'}}));
  } else if (behavior === 'deny-exit') {
    console.error('fixture');
    process.exitCode = 2;
  } else if (behavior === 'error') {
    process.exitCode = 1;
  } else if (behavior === 'timeout') {
    setTimeout(() => {}, 5000);
  } else {
    console.log('{}');
  }
});
