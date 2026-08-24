{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = with pkgs; [ 
    git
    playwright
    playwright-driver
    playwright.browsers
    nodejs
    #PACKAGE_LIST
    ];

  # https://devenv.sh/basics/
  env = {
    PROJ = "webdantic";
    PGHOST = lib.mkForce "127.0.0.1";

    #PLAYWRIGHT_BROWSERS_PATH = pkgs.playwright-driver.browsers;
    PLAYWRIGHT_DRIVER_EXECUTABLE_PATH = "${pkgs.playwright-driver}/bin/playwright-driver";
    PLAYWRIGHT_BROWSERS_PATH          = "${pkgs.playwright.browsers}/share/playwright";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
    PLAYWRIGHT_NODEJS_PATH = "${pkgs.nodejs}/bin/node";
    #PLAYWRIGHT_LAUNCH_OPTIONS_EXECUTABLE_PATH = "${pkgs-playwright.playwright.browsers}/chromium-${chromium-rev}/chrome-linux/chrome";
    #ENVVAR_LIST
    #
    };

  # https://devenv.sh/languages/
  # languages.rust.enable = true;
  languages.python = {
		   enable = true;
		   venv.enable = true;
		
		   uv.enable = true;
		
		 };

  # https://devenv.sh/processes/
  # processes.dev.exec = "${lib.getExe pkgs.watchexec} -n -- ls -la";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts.hello.exec = ''
    echo hello from $GREET
  '';

  # https://devenv.sh/basics/
  enterShell = ''
    echo ""
    hello         # Run scripts directly
    echo ""
    git --version # Use packages
    echo ""
    playwright --version
    echo ""
  '';

  # devman — the automation plane (CONCEPT.md §5). `base` alone: this repository
  # ships no scheduled work and writes none of its own files.
  devman = {
    enable = true;
    project = "webdantic";
    groups = [ "base" ];
  };

  # https://devenv.sh/tasks/
  #
  # base's two names. The group file names a task and never a tool or its
  # arguments, so what each one IS lives here.
  #
  # `base:test` IS NOT `devenv test`. `enterTest` below is still the devenv
  # template's default — it greps `git --version` — so `devenv test` exits 0
  # having tested nothing, which is what PROPOSAL.md §12's fourth rule forbids
  # shipping as a default. The suite is `tests/`, and `pytest` runs it.
  tasks = {
    # `uv run --extra dev`, not a bare `pytest`. This project keeps pytest in
    # `[project.optional-dependencies].dev`, and devenv's venv installs only the
    # base dependencies — a bare `pytest` is `command not found` inside the
    # shell. `uv run --extra dev` resolves the group and runs the suite.
    "webdantic:lint".exec = "ruff check .";
    "webdantic:test".exec = "uv run --extra dev pytest";

    "base:check".after = [ "webdantic:lint" ];
    "base:test".after = [ "webdantic:test" ];
  };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/git-hooks/
  # git-hooks.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
