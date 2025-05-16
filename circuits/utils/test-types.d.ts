declare module 'circom_tester' {
  export function wasm(circuitPath: string): Promise<any>;
}

declare const describe: (description: string, callback: () => void) => void;
declare const before: (callback: () => void) => void;
declare const it: (description: string, callback: () => void) => void;
declare const __dirname: string; 