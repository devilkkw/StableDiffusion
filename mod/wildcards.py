import os
import random
import sys
import tempfile

from modules import scripts, script_callbacks, shared

warned_about_files = {}
wildcard_dir = scripts.basedir()


class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def get_used_lines(self, wildcard):
        used_lines_file = os.path.join(tempfile.gettempdir(), f"used_{wildcard}.txt")
        if os.path.exists(used_lines_file):
            with open(used_lines_file, "r") as f:
                used_lines = set(int(line.strip()) for line in f.readlines())
        else:
            used_lines = set()
        return used_lines

    def save_used_lines(self, wildcard, used_lines):
        used_lines_file = os.path.join(tempfile.gettempdir(), f"used_{wildcard}.txt")
        with open(used_lines_file, "w") as f:
            for line in used_lines:
                f.write(str(line) + "\n")

    def replace_wildcard(self, text, lines, used_lines, gen):
        if " " in text or len(text) == 0:
            return text

        available_lines = set(range(len(lines))) - used_lines
        if len(available_lines) == 0:
            # Reset used lines if all lines have been used
            used_lines = set()
            available_lines = set(range(len(lines)))

        chosen_line = gen.choice(list(available_lines))
        used_lines.add(chosen_line)

        return lines[chosen_line], used_lines

    def process(self, p):
        original_prompt = p.all_prompts[0]

        for i in range(len(p.all_prompts)):
            gen = random.Random()
            gen.seed(p.all_seeds[0 if shared.opts.wildcards_same_seed else i])

            prompt = p.all_prompts[i]

            wildcard_chunks = prompt.split("__")
            for j in range(1, len(wildcard_chunks), 2):
                wildcard = wildcard_chunks[j]
                replacement_file = os.path.join(wildcard_dir, "wildcards", f"{wildcard}.txt")
                if os.path.exists(replacement_file):
                    with open(replacement_file, encoding="utf8") as f:
                        lines = f.read().splitlines()

                    used_lines = self.get_used_lines(wildcard)

                    chosen_line, used_lines = self.replace_wildcard(wildcard, lines, used_lines, gen)
                    wildcard_chunks[j] = chosen_line

                    self.save_used_lines(wildcard, used_lines)

            prompt = "".join(wildcard_chunks)
            p.all_prompts[i] = prompt

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt


def on_ui_settings():
    shared.opts.add_option("wildcards_same_seed", shared.OptionInfo(False, "Use same seed for all images", section=("wildcards", "Wildcards")))


script_callbacks.on_ui_settings(on_ui_settings)
