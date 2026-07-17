import fs from "fs";
import path from "path";
import yaml from "js-yaml";

export type AgentConfig = {
  issues: {
    auto_process_labels: string[];
    skip_labels: string[];
  };
  code_quality: {
    min_coverage: number;
    auto_fix: boolean;
    max_complexity: number;
  };
  schedule: {
    nightly: {
      enabled: boolean;
      time: string;
    };
  };
  pr: {
    draft_for_complex_changes: boolean;
    complex_change_threshold: number;
  };
  metrics: {
    enabled: boolean;
    track: string[];
  };
};

export function loadConfig(): AgentConfig {
  const configPath = path.join(process.cwd(), ".github", "copilot-agent-config.yml");
  const raw = fs.readFileSync(configPath, "utf8");
  const parsed = yaml.load(raw) as AgentConfig;
  return parsed;
}

export function printConfig() {
  const config = loadConfig();
  console.log(JSON.stringify(config, null, 2));
}
