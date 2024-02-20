{{/*
Expand the name of the chart.
*/}}
{{- define "tzkt.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "tzkt.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "tzkt.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "tzkt.labels" -}}
helm.sh/chart: {{ include "tzkt.chart" . }}
{{ include "tzkt.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "tzkt.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tzkt.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "tzkt.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "tzkt.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* tzkt db connection string */}}
{{- define "tzkt.connectionString" -}}
{{ print " " "server=$(POSTGRES_HOST);port=$(POSTGRES_PORT);database=$(POSTGRES_DB);username=$(POSTGRES_USER);password=$(POSTGRES_PASSWORD);command timeout=$(POSTGRES_COMMAND_TIMEOUT);" }}
{{- end -}}

{{/* tzkt api httl url */}}
{{- define "tzkt.apiUrl" -}}
{{ print "http://0.0.0.0:%s" .Values.api.port }}
{{- end -}}