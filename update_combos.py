import sys

with open(r'C:\Users\gian9\OneDrive\Desktop\Proyecto Papi\dashboard_ventas.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert HTML for combinations section
tips_section_html = """    <!-- Tips de rentabilidad -->
    <div class="rentabilidad-section">
      <div class="section-heading">Estrategia</div>
      <div class="section-title">Ideas para mejorar la rentabilidad 💡</div>
      <div class="tips-grid" id="tips-grid">
        <!-- Tips dinámicos -->
      </div>
    </div>"""

combos_section_html = tips_section_html + """

    <!-- Combos section -->
    <div class="table-card" id="combos-section-container" style="display: none;">
      <div class="chart-title">Análisis de Órdenes</div>
      <div class="chart-heading" style="margin-bottom:1rem">Productos combinados frecuentemente</div>
      <table>
        <thead>
          <tr>
            <th>Combinación detectada</th>
            <th class="right">Frecuencia</th>
            <th>Sugerencia</th>
          </tr>
        </thead>
        <tbody id="tabla-combos"></tbody>
      </table>
    </div>"""

content = content.replace(tips_section_html, combos_section_html)

# 2. Add generateCombinationsTable function call in processData
update_visuals_call = """  // Update Visuals
  updateTable(sorted, totalMonto);
  generateTips(ventas, sorted, totalMonto);"""

update_visuals_call_new = """  // Update Visuals
  updateTable(sorted, totalMonto);
  generateTips(ventas, sorted, totalMonto);
  generateCombinationsTable(ventas);"""

content = content.replace(update_visuals_call, update_visuals_call_new)

# 3. Add the generateCombinationsTable function and simplify generateTips
generate_tips_code = """  const ordersMap = {};
  ventas.forEach(v => {
    if(v.orden) {
      if(!ordersMap[v.orden]) ordersMap[v.orden] = [];
      if(!ordersMap[v.orden].includes(v.producto)) {
        ordersMap[v.orden].push(v.producto);
      }
    }
  });

  const combinations = {};
  Object.values(ordersMap).forEach(items => {
    if (items.length > 1) {
      const sortedItems = items.slice().sort();
      for (let i = 0; i < sortedItems.length; i++) {
        for (let j = i + 1; j < sortedItems.length; j++) {
          const pair = shortLabel(sortedItems[i], 20) + " + " + shortLabel(sortedItems[j], 20);
          combinations[pair] = (combinations[pair] || 0) + 1;
        }
      }
    }
  });

  const multiItemOrders = Object.values(ordersMap).filter(items => items.length > 1).length;
  
  if (multiItemOrders > 0) {
    const topPair = Object.entries(combinations).sort((a, b) => b[1] - a[1])[0];
    if (topPair && topPair[1] > 1) {
      addTip('🔄', 'El Combo Estrella', `La combinación de <strong>${topPair[0]}</strong> se llevó junta en <strong>${topPair[1]} órdenes</strong>. Considerá armar una promoción o kit para aumentar más tu ticket promedio.`);
    } else {
      addTip('🔄', 'Combos y Bundles', `${multiItemOrders} órdenes tuvieron múltiples productos. Identificar qué artículos se llevan juntos te ayudará a armar promociones efectivas.`);
    }
  } else {
    addTip('🔄', 'Promocioná Combos', 'Casi todas tus ventas son de un solo producto a la vez. Ofrecé artículos complementarios al momento de cobrar para aumentar tu ticket promedio.');
  }"""

generate_tips_code_new = """  // Combo suggestions are now moved to generateCombinationsTable
  // But we keep the basic multi-order tip if they don't have many combos
  const ordersMap = {};
  ventas.forEach(v => {
    if(v.orden) {
      if(!ordersMap[v.orden]) ordersMap[v.orden] = [];
      if(!ordersMap[v.orden].includes(v.producto)) {
        ordersMap[v.orden].push(v.producto);
      }
    }
  });
  const multiItemOrders = Object.values(ordersMap).filter(items => items.length > 1).length;
  if (multiItemOrders === 0) {
    addTip('🔄', 'Promocioná Combos', 'Casi todas tus ventas son de un solo producto a la vez. Ofrecé artículos complementarios al momento de cobrar para aumentar tu ticket promedio.');
  }"""

content = content.replace(generate_tips_code, generate_tips_code_new)

new_function = """
function generateCombinationsTable(ventas) {
  const ordersMap = {};
  ventas.forEach(v => {
    if(v.orden) {
      if(!ordersMap[v.orden]) ordersMap[v.orden] = [];
      if(!ordersMap[v.orden].includes(v.producto)) {
        ordersMap[v.orden].push(v.producto);
      }
    }
  });

  const combinations = {};
  Object.values(ordersMap).forEach(items => {
    if (items.length > 1) {
      const sortedItems = items.slice().sort();
      for (let i = 0; i < sortedItems.length; i++) {
        for (let j = i + 1; j < sortedItems.length; j++) {
          const pair = sortedItems[i] + " y " + sortedItems[j];
          combinations[pair] = (combinations[pair] || 0) + 1;
        }
      }
    }
  });

  const sortedCombos = Object.entries(combinations)
    .filter(([pair, count]) => count > 1)
    .sort((a, b) => b[1] - a[1]);

  const container = document.getElementById('combos-section-container');
  const tbody = document.getElementById('tabla-combos');
  tbody.innerHTML = '';

  if (sortedCombos.length > 0) {
    container.style.display = 'block';
    sortedCombos.forEach((combo, i) => {
      const pairText = combo[0];
      const count = combo[1];
      
      let badge = '';
      if (i === 0) badge = '<span style="background:#dcfce3; color:#166534; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:600;">Combo Estrella</span>';
      
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight:500;">${pairText}</td>
        <td class="right mono"><span style="background:var(--surface2); padding:3px 8px; border-radius:12px; font-weight:600; color:var(--accent);">${count} veces</span></td>
        <td style="color:var(--muted); font-size:0.8rem;">¡Crea un combo con estos dos! ${badge}</td>
      `;
      tbody.appendChild(tr);
    });
  } else {
    container.style.display = 'none';
  }
}
"""

# Insert the new function right before the closing script tag
content = content.replace('</script>', new_function + '\n</script>')

with open(r'C:\Users\gian9\OneDrive\Desktop\Proyecto Papi\dashboard_ventas.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated combinations section successfully.")
