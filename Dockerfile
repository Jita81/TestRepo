# Multi-stage build for production

# Stage 1: Base
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./

# Stage 2: Dependencies
FROM base AS dependencies
RUN npm ci --only=production
RUN cp -R node_modules prod_node_modules
RUN npm ci

# Stage 3: Build
FROM base AS build
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm test

# Stage 4: Production
FROM node:18-alpine AS production
WORKDIR /app

# Install dumb-init to handle signals properly
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy production dependencies
COPY --from=dependencies /app/prod_node_modules ./node_modules

# Copy application files
COPY --chown=nodejs:nodejs backend ./backend
COPY --chown=nodejs:nodejs frontend ./frontend
COPY --chown=nodejs:nodejs package.json ./

# Set environment
ENV NODE_ENV=production
ENV PORT=3000

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "backend/server.js"]