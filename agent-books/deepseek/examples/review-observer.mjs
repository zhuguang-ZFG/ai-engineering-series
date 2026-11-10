/** Original book plugin. The recorder belongs to its caller, not to Cordis. */
export function reviewObserver(record) {
  return Object.assign(function bookReviewObserver(ctx) {
    record("observer:load");
    ctx.effect(() => {
      record("resource:open");
      return async () => {
        await Promise.resolve();
        record("resource:closed");
      };
    });
    ctx.on("book/review", (file) => {
      record(`review:${ctx.bookCounter.next()}:${file}`);
    });
  }, { inject: ["bookCounter"] });
}

/** Around-middleware must return next()'s result, including its promise. */
export function reviewWrapper(label, record) {
  return function bookReviewWrapper(ctx) {
    ctx.on("book/dispatch", async (request, next) => {
      record(`${label}:before:${request.file}`);
      const result = await next();
      record(`${label}:after`);
      return result;
    });
  };
}
