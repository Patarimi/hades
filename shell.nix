#!/usr/bin/env nix-shell
let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShellNoCC {
  packages = with pkgs; [
    magic-vlsi
  ];

  PDK_ROOT= builtins.toString ./pdk;
}
