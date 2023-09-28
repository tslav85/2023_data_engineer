-- public.trascheev_project_ssls definition

-- Drop table

-- DROP TABLE public.trascheev_project_ssls;

CREATE TABLE public.trascheev_project_ssls (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	status int4 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;