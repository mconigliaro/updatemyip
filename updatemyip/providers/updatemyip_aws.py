import boto3
import botocore.client as bc
import botocore.exceptions as be
import logging as log
import updatemyip.exceptions as exc
import updatemyip.provider as pro


class Route53(pro.DNSProvider):

    def options_pre(self, parser):
        parser.add_argument("--aws-route53-hosted-zone-id")

    def options_post(self, parser, options):
        required = ["aws_route53_hosted_zone_id"]
        missing = ", ".join(f"--{opt.replace('_', '-')}"
                            for opt in required
                            if not getattr(options, opt))
        if missing:
            parser.error(f"Missing required aws.Route53 option(s): {missing}")

    def check(self, options, address):
        if options.fqdn.endswith("."):
            fqdn = options.fqdn
        else:
            fqdn = f"{options.fqdn}."
        records = [{"Value": address}]

        self.changes = []

        try:
            config = bc.Config(connect_timeout=options.timeout,
                               retries={'max_attempts': 0})
            self.client = boto3.client("route53", config=config)
            rrsets = self.client.list_resource_record_sets(
                HostedZoneId=options.aws_route53_hosted_zone_id,
                StartRecordName=fqdn,
                MaxItems="1",
            )["ResourceRecordSets"]

        except (be.ConnectionError, be.ClientError) as e:
            raise exc.ProviderError(e) from e

        if rrsets and rrsets[0]["Name"] == fqdn:
            cur_name = rrsets[0]["Name"].rstrip(".")
            cur_ttl = rrsets[0]["TTL"]
            cur_type = rrsets[0]["Type"]
            cur_records = rrsets[0]["ResourceRecords"]
            cur_address = " ".join(r["Value"] for r in cur_records)
            cur_record = f"{cur_name} {cur_ttl} {cur_type} {cur_address}"
            log.info(
                f"Current DNS record: {cur_record}"
            )

            if cur_type != options.dns_rrtype:
                self.changes.append({
                    "Action": "DELETE",
                    "ResourceRecordSet": rrsets[0]
                })
            elif cur_ttl == options.dns_ttl and cur_records == records:
                return False
        else:
            log.info(f"DNS record not found: {options.fqdn}")

        self.changes.append({
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": fqdn,
                "Type": options.dns_rrtype,
                "TTL": options.dns_ttl,
                "ResourceRecords": records,
            },
        })

        return True

    def update(self, options, address):
        try:
            self.client.change_resource_record_sets(
                HostedZoneId=options.aws_route53_hosted_zone_id,
                ChangeBatch={"Changes": self.changes},
            )

        except (be.ConnectionError, be.ClientError) as e:
            raise exc.ProviderError(e) from e

        return True