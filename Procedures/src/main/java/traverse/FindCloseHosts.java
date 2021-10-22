package traverse;

import org.neo4j.graphdb.*;
import org.neo4j.graphdb.traversal.*;
import org.neo4j.procedure.*;

import java.util.stream.Stream;
import java.util.stream.StreamSupport;


public class FindCloseHosts {

    // node labels
    static final Label IP = Label.label("IP");
    static final Label OrganizationUnit = Label.label("OrganizationUnit");
    static final Label Contact = Label.label("Contact");

    // relationship types
    static final RelationshipType HAS = RelationshipType.withName("HAS");
    static final RelationshipType PART_OF = RelationshipType.withName("PART_OF");

    @Context
    public Transaction tx;

    /**
     * Traverse from attacked host's IP and finds IP of close hosts, to maximum depth given as a parameter.
     * Evaluates traversed path with weight.
     * @param ip Attacked host's IP
     * @param maxDepth Maximum depth to traverse
     * @return Stream of FindCloseHostsRecord containing ip node, path weight and distance
     */
    @Procedure(value = "traverse.findCloseHosts", mode = Mode.READ)
    @Description("traverse starting from the node with the given IP address and returns all close IPs")
    public Stream<FindCloseHostsRecord> findCloseHosts(@Name("ipAddress") String ip,
                                                       @Name("maxDepth") Long maxDepth) {

        // find attacked host IP node
        Node attackedHost = tx.findNodes(IP, "address", ip)
                .stream()
                .findFirst()
                .orElseThrow(IllegalArgumentException::new);

        // BFS from given host
        final Traverser traverse = tx.traversalDescription()
                .breadthFirst()
                .relationships(HAS, Direction.BOTH)
                .relationships(PART_OF, Direction.BOTH)
                .evaluator(Evaluators.fromDepth(1))
                .evaluator(Evaluators.toDepth(maxDepth.intValue()))
                .evaluator(Evaluators.includeIfAcceptedByAny(new LabelEvaluator(IP)))
                .traverse(attackedHost);

        // Map path to result records.
        return StreamSupport
                .stream(traverse.spliterator(), true)
                .map(FindCloseHostsRecord::new);
    }


    /**
     * Result record
     */
    public static final class FindCloseHostsRecord {

        public final Node ip;
        public final Long distance;
        public final String path_type;

        FindCloseHostsRecord(Path path) {
            this.ip = path.endNode();
            this.distance = (long) path.length();
            this.path_type = EvaluatePath(path.nodes());
        }

        // determines type of the path (over contact, subnet...)
        public String EvaluatePath(Iterable<Node> nodes) {
            for (Node node : nodes) {
                if (node.hasLabel(OrganizationUnit)) {
                    return "organization";
                } else if (node.hasLabel(Contact)) {
                    return "contact";
                }
            }

            return "subnet";
        }
    }

    /**
     * Evaluator for node's labels.
     */
    private static final class LabelEvaluator implements Evaluator {

        private final Label label;

        private LabelEvaluator(Label label) {
            this.label = label;
        }

        @Override
        public Evaluation evaluate(Path path) {
            if (path.endNode().hasLabel(label)) {
                return Evaluation.INCLUDE_AND_CONTINUE;
            } else {
                return Evaluation.EXCLUDE_AND_CONTINUE;
            }
        }
    }
}
