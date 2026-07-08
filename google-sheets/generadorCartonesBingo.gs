function generarCartonesVisuales() {
  const hojaOrigen = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Cartones texto");
  if (!hojaOrigen) {
    SpreadsheetApp.getUi().alert("No se encuentra la hoja 'Cartones texto'. Revisa el nombre o anadela.");
    return;
  }

  const datos = hojaOrigen.getDataRange().getValues();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const hojaNueva = ss.getSheetByName("Cartones visual") || ss.insertSheet("Cartones visual");
  hojaNueva.clear();

  let fila = 1;
  let columna = 1;

  for (let i = 1; i < datos.length; i++) {
    const carton = datos[i];

    const celdaTitulo = hojaNueva.getRange(fila, columna, 1, 4);
    celdaTitulo.merge();
    celdaTitulo.setValue("Bingo Musical");
    celdaTitulo.setFontWeight("bold");
    celdaTitulo.setHorizontalAlignment("center");
    celdaTitulo.setVerticalAlignment("middle");
    celdaTitulo.setFontSize(15);
    celdaTitulo.setBackground("#000000");
    celdaTitulo.setFontColor("white");
    hojaNueva.setRowHeight(fila, 50);

    for (let j = 0; j < 3; j++) {
      for (let k = 0; k < 4; k++) {
        const index = j * 4 + k;
        const celda = hojaNueva.getRange(fila + j + 1, columna + k);
        celda.setValue(carton[index]);
        celda.setBorder(true, true, true, true, true, true);
        celda.setHorizontalAlignment("center");
        celda.setVerticalAlignment("middle");
        celda.setFontSize(11);
        celda.setFontWeight("bold");
        celda.setWrap(true);
        celda.setBackground("#ffffff");

        const colActual = columna + k;
        if (colActual !== 5) {
          hojaNueva.setColumnWidth(colActual, 110);
        }

        hojaNueva.setRowHeight(fila + j + 1, 100);
      }
    }

    if (columna === 1) {
      columna = 6;
    } else {
      columna = 1;
      fila += 6;
    }
  }
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("Gestion Cartones Bingo")
    .addItem("Generar Cartones Visuales", "generarCartonesVisuales")
    .addToUi();
}
