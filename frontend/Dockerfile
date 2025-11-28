FROM rustlang/rust:nightly AS wasm
WORKDIR /src
RUN cargo install wasm-pack --version 0.12.1
COPY wasm ./wasm
RUN cd wasm && wasm-pack build --release --target web --out-dir /tmp/pkg

FROM node:18-alpine AS deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend .
COPY --from=wasm /tmp/pkg ./src/wasm/pkg
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
RUN npm install -g serve
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]

