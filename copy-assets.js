const fs = require("fs");

const srcDir = "src/assets/";
const destDir = "static/assets/";

if (!fs.existsSync(destDir)){
    fs.mkdirSync(destDir, { recursive: true });
}

if (fs.existsSync(srcDir)) {
    fs.cpSync(srcDir, destDir, { recursive: true });
    console.log(`Copied all files from ${srcDir} to ${destDir}`);
} else {
    console.warn(`Warning: Source directory "${srcDir}" not found.`);
}
