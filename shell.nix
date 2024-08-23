#!/usr/bin/env nix-shell
let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShellNoCC {
  packages = with pkgs; [
    magic-vlsi
  ];

  shellHook =
      ''export PDK_ROOT="$(pwd)/pdk"'';
}
