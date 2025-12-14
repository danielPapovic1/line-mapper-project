public class Example04 {
    private int alpha = 9;
    private int beta = 14;
    private int gamma = 19;
    private String name;
    public Example04() {
        name = "Example04";
        System.out.println("init " + name);
        System.out.println("alpha ready");
        System.out.println("beta ready");
    }
    public int sum() {
        int total = alpha + beta + gamma + 4;
        System.out.println("sum=" + total);
        return total;
    }
    public int diff() {
        int delta = gamma - alpha;
        System.out.println("diff updated for Example04: " + delta);
        return delta;
    }
    public void status() {
        System.out.println("alpha=" + alpha);
        System.out.println("beta=" + beta);
        System.out.println("gamma=" + gamma);
        System.out.println("done");
    }
    public void debug() {
        for (int i = 0; i < 3; i++) {
            System.out.println("debug#" + i);
        }
    }
}
