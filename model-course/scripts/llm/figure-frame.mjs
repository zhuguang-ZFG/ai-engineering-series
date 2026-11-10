// Shared paper and frame for every course figure. The drawings keep their own
// geometry; this only adds the quiet paper grain, hairline frame and corner
// registration marks that make a page of diagrams read as one printed set.
const ink = "#1f2328";
const paper = "#fbfaf6";

export function artDefs() {
  return `<defs><pattern id="figure-grain" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r=".7" fill="${ink}" opacity=".16"/><circle cx="12" cy="13" r=".55" fill="${ink}" opacity=".11"/></pattern></defs>`;
}

export function artPaper(width, height) {
  return `<rect width="${width}" height="${height}" fill="${paper}"/>` +
    `<rect width="${width}" height="${height}" fill="url(#figure-grain)" opacity=".34"/>` +
    `<rect x="9" y="9" width="${width - 18}" height="${height - 18}" fill="none" stroke="${ink}" stroke-width=".8" opacity=".22"/>` +
    `<path d="M9 30 V9 H30 M${width - 30} 9 H${width - 9} V30 M9 ${height - 30} V${height - 9} H30 M${width - 30} ${height - 9} H${width - 9} V${height - 30}" fill="none" stroke="${ink}" stroke-width="1.2" opacity=".38"/>`;
}
