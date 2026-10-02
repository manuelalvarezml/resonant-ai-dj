const paths = {
 play:'m9 5 11 7-11 7Z', pause:'M8 5v14M16 5v14', next:'m5 5 10 7-10 7ZM19 5v14', previous:'m19 5-10 7 10 7ZM5 5v14',
 search:'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0', library:'M4 5v15M9 5v15M15 5l5 14',
 heart:'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',
 plus:'M12 5v14M5 12h14', close:'m6 6 12 12M6 18 18 6', arrow:'M5 12h14m-6-6 6 6-6 6',
 shuffle:'m3 4 4 0 10 16h4m-4-4 4 4-4 3M3 20h4l3-5m3-6 4-5h4m-4-3 4 3-4 4', repeat:'M4 7h13l3 3m-3-6 3 3-3 3M20 17H7l-3-3m3 6-3-3 3-3',
 queue:'M4 5h16M4 11h16M4 17h9m4-3 4 3-4 3', volume:'M11 4 5 9H2v6h3l6 5ZM15 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14', mute:'M11 4 5 9H2v6h3l6 5Zm5 5 6 6m-6 0 6-6',
 more:'M4 12h.01M12 12h.01M20 12h.01', clock:'M12 8v4l3 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
 music:'M9 18V5l12-2v12M9 8l12-2M9 18a3 3 0 1 1-3-3h3M21 15a3 3 0 1 1-3-3h3',
 analyze:'M3 12h3l2-6 3 12 3-12 2 6h5', columns:'M4 5h16v14H4ZM10 5v14M16 5v14',
 info:'M12 11v6M12 7h.01M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
 down:'m6 9 6 6 6-6', up:'m6 15 6-6 6 6', check:'m5 12 4 4L19 6', trash:'M3 6h18M8 6V3h8v3M5 6l1 15h12l1-15M10 10v7M14 10v7', download:'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4', refresh:'M20 7v5h-5M4 17v-5h5M5 7a8 8 0 0 1 14 0m0 10a8 8 0 0 1-14 0'
};
export const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${name==='brand'?'<path d="M4 8v8M9 4v16M14 7v10M19 10v4" stroke-width="3"/>':`<path d="${paths[name] ?? paths.music}"/>`}</svg>`;
