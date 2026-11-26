import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const sharp = require('C:/Users/zicza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const output = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../Reports/Figures_Thesis');
const previews = path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'previews');
fs.mkdirSync(previews, {recursive:true});
for (const file of fs.readdirSync(output).filter(n => n.endsWith('.svg'))) {
  const svg = path.join(output, file);
  const png = svg.replace(/\.svg$/,'.png');
  await sharp(svg, {density:144}).png().withMetadata({density:300}).toFile(png);
  await sharp(png).resize({width:1100}).png().toFile(path.join(previews,file.replace(/\.svg$/, '_preview.png')));
  const info = await sharp(png).metadata();
  console.log(`${path.basename(png)}: ${info.width} x ${info.height}`);
}
