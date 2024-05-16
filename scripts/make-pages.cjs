const fs = require("node:fs");
const path = require("node:path");
const ejs = require("ejs");

const utf8 = "utf8";

const dataDir = "data";
const templatesDir = "templates";
const staticDir = "docs";

const tokensDataPath = path.join(dataDir, "tokens.json");
const indexTemplatePath = path.join(templatesDir, "index.ejs");
const tokenTemplatePath = path.join(templatesDir, "token.ejs");
const indexPagePath = path.join(staticDir, "index.html");
const tokenPagePath = (ticker) => path.join(staticDir, `${ticker}.html`);

fs.readFile(tokensDataPath, utf8, (err, data) => {
	if (err) {
		console.error(err);
		return;
	}

	const tokens = JSON.parse(data);

	fs.readFile(tokenTemplatePath, utf8, (err, template) => {
		if (err) {
			console.error(err);
			return;
		}

		tokens.forEach((token) => {
			const tokenHtml = ejs.render(template, token);
			fs.writeFile(tokenPagePath(token.ticker), tokenHtml, (err) => {
				if (err) {
					console.error(err);
					return;
				}
				console.log(`HTML file ${token.ticker}.html has been generated.`);
			});
		});
	});

	fs.readFile(indexTemplatePath, utf8, (err, template) => {
		if (err) {
			console.error(err);
			return;
		}

		const indexHtml = ejs.render(template, { tokens });
		fs.writeFile(indexPagePath, indexHtml, (err) => {
			if (err) {
				console.error(err);
				return;
			}
			console.log("HTML file index.html has been generated.");
		});
	});
});
