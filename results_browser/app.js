// Sortable tables: click a header; numbers come from data-v when present.
document.querySelectorAll("table.sortable").forEach(function (table) {
  table.querySelectorAll("th").forEach(function (th, col) {
    th.addEventListener("click", function () {
      var asc = !th.classList.contains("asc");
      table.querySelectorAll("th").forEach(function (h) { h.classList.remove("asc", "desc"); });
      th.classList.add(asc ? "asc" : "desc");
      var body = table.tBodies[0];
      var rows = Array.from(body.rows);
      rows.sort(function (a, b) {
        var x = cellValue(a.cells[col]), y = cellValue(b.cells[col]);
        if (typeof x === "number" && typeof y === "number") return asc ? x - y : y - x;
        return asc ? String(x).localeCompare(String(y)) : String(y).localeCompare(String(x));
      });
      rows.forEach(function (r) { body.appendChild(r); });
    });
  });
});

function cellValue(cell) {
  var v = cell.dataset.v;
  if (v !== undefined && v !== "" && !isNaN(parseFloat(v))) return parseFloat(v);
  if (v === "") return Infinity;  // missing values sort last (ascending)
  return cell.textContent.trim().toLowerCase();
}

// Study page: switch between transcripts.
var picker = document.getElementById("transcript-select");
if (picker) {
  picker.addEventListener("change", function () {
    document.querySelectorAll(".transcript").forEach(function (t) { t.hidden = t.id !== picker.value; });
  });
}

// Landing page: equation toggles (KaTeX renders on first open; raw LaTeX stays if KaTeX did not load).
document.querySelectorAll(".eq-toggle").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var row = document.getElementById(btn.dataset.target);
    row.hidden = !row.hidden;
    btn.setAttribute("aria-expanded", String(!row.hidden));
    if (!row.hidden && window.katex && !row.dataset.rendered) {
      row.querySelectorAll(".tex").forEach(function (el) {
        katex.render(el.textContent, el, { displayMode: true, throwOnError: false });
      });
      row.dataset.rendered = "1";
    }
  });
});

// Landing page: experiment map.
var mapEl = document.getElementById("map");
var highlighted = null;  // paradigm group index picked in the legend
if (mapEl) {
  var data = JSON.parse(document.getElementById("map-data").textContent);
  var tip = document.getElementById("map-tip");
  var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  var groupColor = function (g) { var grp = data.groups[g < 0 ? data.groups.length - 1 : g]; return dark ? grp.dark : grp.light; };
  var NS = "http://www.w3.org/2000/svg";
  var svg = document.createElementNS(NS, "svg");
  mapEl.appendChild(svg);
  var circles = [];
  var screen = [];  // pixel positions for hit-testing

  var draw = function () {
    var w = mapEl.clientWidth, h = Math.max(320, Math.min(520, w * 0.55)), pad = 18;
    svg.setAttribute("width", w); svg.setAttribute("height", h);
    var xs = data.points.map(function (p) { return p.x; }), ys = data.points.map(function (p) { return p.y; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    screen = data.points.map(function (p) {
      return [pad + (p.x - x0) / (x1 - x0) * (w - 2 * pad), h - pad - (p.y - y0) / (y1 - y0) * (h - 2 * pad)];
    });
    if (!circles.length) {
      // "other" first so the colored points sit on top
      var order = data.points.map(function (p, i) { return i; }).sort(function (a, b) {
        return (data.points[a].group < 0 ? -1 : 0) - (data.points[b].group < 0 ? -1 : 0);
      });
      circles = new Array(data.points.length);
      order.forEach(function (i) {
        var c = document.createElementNS(NS, "circle");
        c.setAttribute("r", 5);
        c.setAttribute("fill", groupColor(data.points[i].group));
        c.setAttribute("class", "pt");
        svg.appendChild(c);
        circles[i] = c;
      });
    }
    circles.forEach(function (c, i) { c.setAttribute("cx", screen[i][0]); c.setAttribute("cy", screen[i][1]); });
  };
  draw();
  window.addEventListener("resize", draw);

  var nearest = function (ev) {
    var r = svg.getBoundingClientRect(), mx = ev.clientX - r.left, my = ev.clientY - r.top, best = -1, bd = 400;  // 20 px radius
    screen.forEach(function (s, i) {
      if (circles[i].classList.contains("dim")) return;
      var d = (s[0] - mx) * (s[0] - mx) + (s[1] - my) * (s[1] - my);
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  };
  var active = -1;
  svg.addEventListener("mousemove", function (ev) {
    var i = nearest(ev);
    if (active >= 0) circles[active].classList.remove("hover");
    active = i;
    svg.style.cursor = i >= 0 ? "pointer" : "default";
    if (i < 0) { tip.hidden = true; return; }
    var p = data.points[i];
    circles[i].classList.add("hover");
    var nll = function (v) { return v == null ? "–" : v.toFixed(3); };
    tip.innerHTML = "<b>" + p.study + "</b> · " + p.exp +
      '<div><span class="sw" style="background:' + groupColor(p.group) + '"></span>' + p.paradigm + "</div>" +
      "<div>" + p.task + (p.participants ? " · " + p.participants.toLocaleString() + " participants" : "") + "</div>" +
      '<div class="tip-nll">Study test NLL (avg): CORE ' + nll(p.core) + " · Transformer " + nll(p.transformer) + "</div>";
    tip.hidden = false;
    var left = screen[i][0] + 14, top = screen[i][1] + 14;
    if (left + tip.offsetWidth > mapEl.clientWidth) left = screen[i][0] - tip.offsetWidth - 14;
    tip.style.left = (mapEl.offsetLeft + left) + "px"; tip.style.top = (mapEl.offsetTop + top) + "px";
  });
  svg.addEventListener("mouseleave", function () {
    tip.hidden = true;
    if (active >= 0) circles[active].classList.remove("hover");
    active = -1;
  });
  svg.addEventListener("click", function (ev) {
    var i = nearest(ev);
    if (i >= 0) window.location.href = "studies/" + data.points[i].study + ".html";
  });

  // Legend: click to highlight one paradigm group.
  var legend = document.getElementById("map-legend");
  data.groups.forEach(function (g, gi) {
    var idx = gi === data.groups.length - 1 ? -1 : gi;
    var b = document.createElement("button");
    b.className = "legend-item";
    b.innerHTML = '<span class="sw" style="background:' + groupColor(idx) + '"></span>' + g.name + ' <span class="n">' + g.n + "</span>";
    b.addEventListener("click", function () {
      highlighted = highlighted === idx ? null : idx;
      legend.querySelectorAll(".legend-item").forEach(function (x) { x.classList.remove("on"); });
      if (highlighted !== null) b.classList.add("on");
      updateMap();
    });
    legend.appendChild(b);
  });
}

// Dim map points outside the legend highlight.
function updateMap() {
  circles.forEach(function (c, i) {
    c.classList.toggle("dim", highlighted !== null && data.points[i].group !== highlighted);
  });
}
