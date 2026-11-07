// One set of unfamiliar tasks drives the web page, book appendix and print pack.
export function reviewTasks(data, h) {
  return data.tasks.map(task => `<section class="review-task" id="${h(task.id)}"><p class="eyebrow">${h(task.id)} · 换材料练习</p><h2>${h(task.title)}</h2>${task.material.map(text => `<p>${h(text)}</p>`).join("")}${(task.documents ?? []).map(id => {
    const doc = data.documents.find(item => item.id === id);
    if (!doc) throw new Error(`Review task ${task.id}: missing ${id}`);
    return `<blockquote class="review-document" id="review-${h(id)}"><h3>${h(doc.id)} · ${h(doc.title)}</h3><p>${h(doc.text)}</p></blockquote>`;
  }).join("")}<ol>${task.questions.map(text => `<li>${h(text)}</li>`).join("")}</ol><div class="answer-space" aria-label="纸上作答区"><p>${h(task.answerLabel)}</p>${Array.from({ length: task.lines }, () => '<div class="answer-line" aria-hidden="true">&#160;</div>').join("")}</div></section>`).join("\n");
}

export function reviewRubric(data, rubric, h) {
  return rubric.criteria.map(item => {
    const task = data.tasks.find(task => task.id === item.task);
    if (!task) throw new Error(`Review rubric: missing task ${item.task}`);
    return `<section class="review-rubric" id="rubric-${h(task.id)}"><h2>${h(task.id)} · ${h(task.title)}</h2><h3>需要看到什么</h3><ul>${item.mustInclude.map(text => `<li>${h(text)}</li>`).join("")}</ul><p><strong>一种答法：</strong>${h(item.example)}</p><p><strong>卡住后的提示：</strong>${h(item.hint)}</p></section>`;
  }).join("\n");
}

export function reviewRecord(data, course) {
  return {
    schemaVersion: "1.0.0",
    courseVersion: course.version,
    taskVersion: data.version,
    participantCode: "",
    sessionDate: "",
    stage: null,
    stageOptions: ["起步试读", "完整课程"],
    readingFormat: "",
    initialFamiliarity: "",
    statusOptions: ["独立完成", "看提示完成", "未完成"],
    note: "空白模板，非试读结果。未做题保持 status 为 null；首次答案与修改后答案分开保存。",
    tasks: data.tasks.map(task => ({
      id: task.id,
      objective: task.objective,
      status: null,
      firstAnswer: "",
      readerWords: "",
      stuckAt: "",
      hints: [],
      rationale: "",
      revisedAnswer: ""
    })),
    objectives: { O1: null, O2: null, O3: null, O4: null, O5: null },
    coreIndependent: null,
    endedEarly: null,
    followUp: ""
  };
}

export function reviewPaperRecord(data, h) {
  return `<section class="review-record" id="record"><h2>一位读者的空白记录表</h2><p>匿名编号：________　日期：________</p><p>阶段：起步试读 / 完整课程　阅读方式：网页 / PDF / EPUB</p><p>已有经验：________________　是否中途结束：________</p><p>每题状态填写“独立完成 / 看提示完成 / 未完成”，未做保留空白。首次答案保留在练习纸或独立文件中。</p>${data.tasks.map(task => `<section class="record-task"><h3>${h(task.id)} · ${h(task.title)}</h3><p>状态：________________</p><p>卡点位置与原话：________________________________</p><p>提示原话与次数：________________________________</p><p>判断依据 / 首次答案存放处：______________________</p><p>修改后表现另记：________________________________</p></section>`).join("")}<h3>按目标汇总，先核对首次表现</h3><p>O1（R01、R02）：______　O2（R03）：______　O3（R04）：______</p><p>O4（R05）：______　O5（R06，单列）：______</p><p>O1–O4 是否全部独立完成：______　复核人：______</p><p>只汇总实际记录；空白和未完成不能记为独立完成。</p></section>`;
}
